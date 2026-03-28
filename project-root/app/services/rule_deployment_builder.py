import re

from infrastructure.file_loader.registry_loader import RegistryLoader


class RuleDeploymentBuilder:
    """Resolve ingest targets and build deployment payloads for rendered rules."""

    def __init__(self, registry_loader: RegistryLoader) -> None:
        """Store registry loader used as a fallback for ingest target resolution."""
        self.registry_loader = registry_loader

    def build(self, tenant, exported_rules: list[dict]) -> tuple[list[dict], dict]:
        """Return rule payloads with resolved targets plus one deployment manifest."""
        mapped_rules: list[dict] = []
        deployments: list[dict] = []
        seen_rule_ids: set[str] = set()
        existing_enabled_by_rule_id = {
            item.rule_id: item.enabled for item in (tenant.rule_deployments or []) if item.rule_id
        }

        for item in exported_rules:
            mapped = dict(item)
            rule_id = mapped.get("id")
            if not rule_id or rule_id in seen_rule_ids:
                continue
            seen_rule_ids.add(rule_id)
            mapping = self._resolve_mapping(tenant, mapped)
            mapped = self._apply_mapping(mapped, mapping)
            mapped_rules.append(mapped)
            deployments.append(
                {
                    "rule_id": rule_id,
                    "enabled": existing_enabled_by_rule_id.get(rule_id, True),
                    "display_name": mapped.get("display_name") or mapped.get("id"),
                }
            )

        payload = {
            "schema_version": 1.0,
            "tenant_id": tenant.tenant_id,
            "rule_deployments_by_siem": {tenant.siem_id or "": deployments},
        }
        return mapped_rules, payload

    def _resolve_mapping(self, tenant, item: dict) -> dict:
        """Resolve the effective ingest targets for one rendered rule candidate."""
        targets = item.get("targets") or {}
        if self._has_explicit_targets(targets):
            return self._normalize_existing_targets(targets)

        ingest_targets = self._collect_ingest_targets(tenant, item)
        if not ingest_targets:
            return {}

        indexes = sorted({target["index"] for target in ingest_targets if target.get("index")})
        sourcetypes = sorted(
            {target["sourcetype"] for target in ingest_targets if target.get("sourcetype")}
        )

        mapping: dict = {"ingest_targets": ingest_targets}
        if len(indexes) == 1:
            mapping["index"] = indexes[0]
        if len(sourcetypes) == 1:
            mapping["sourcetype"] = sourcetypes[0]
        return mapping

    def _apply_mapping(self, item: dict, mapping: dict) -> dict:
        """Apply resolved ingest targets to the flat rendered-rule payload."""
        if not mapping:
            return item

        targets = dict(item.get("targets") or {})
        ingest_targets = mapping.get("ingest_targets") or []
        if ingest_targets:
            # Preserve the fully expanded target list for rules that map to multiple datasets.
            targets["ingest_targets"] = ingest_targets

        index = mapping.get("index")
        sourcetype = mapping.get("sourcetype")
        if index and not targets.get("index"):
            targets["index"] = index
        if sourcetype and not targets.get("sourcetype"):
            targets["sourcetype"] = sourcetype
        item["targets"] = targets

        query = item.get("search_query")
        if isinstance(query, str):
            query = self._apply_query_targets(query, mapping)
            item["search_query"] = query
        return item

    def _has_explicit_targets(self, targets: dict) -> bool:
        """Return True when a rule payload already includes concrete ingest targets."""
        return bool(targets.get("index") or targets.get("sourcetype") or targets.get("ingest_targets"))

    def _normalize_existing_targets(self, targets: dict) -> dict:
        """Normalize pre-existing targets into the shape expected by downstream services."""
        normalized = dict(targets)
        ingest_targets = normalized.get("ingest_targets")
        if isinstance(ingest_targets, list):
            normalized["ingest_targets"] = [item for item in ingest_targets if isinstance(item, dict)]
        return normalized

    def _collect_ingest_targets(self, tenant, item: dict) -> list[dict]:
        """Collect tenant ingest bindings whose device and dataset match one source rule."""
        rule_category = self._normalize_value(item.get("category"))
        rule_product = self._normalize_value(item.get("product"))
        rule_service = self._normalize_value(item.get("service") or item.get("dataset"))
        resolved_targets: list[dict] = []
        seen_targets: set[tuple[str | None, str | None, str, str]] = set()

        for device_id, device in tenant.devices.items():
            if not self._device_matches_rule(device, rule_product):
                continue

            logsource = tenant.logsources.get(device_id)
            binding = tenant.bindings.get(device_id)
            if logsource is None or binding is None:
                continue

            for dataset in logsource.datasets or []:
                if not isinstance(dataset, dict):
                    continue
                if not self._dataset_matches_rule(device, dataset, rule_category, rule_service):
                    continue

                dataset_key = dataset.get("dataset_id") or dataset.get("service_id")
                if not dataset_key:
                    continue

                bind_cfg = binding.bindings.get(dataset_key) or {}
                index = bind_cfg.get("index")
                sourcetype = bind_cfg.get("sourcetype")
                if not index and not sourcetype:
                    fallback_cfg = self.registry_loader.resolve_siem_config(
                        vendor=device.vendor,
                        product=device.product,
                        siem_id=tenant.siem_id or "",
                    )
                    index = fallback_cfg.get("index")
                    sourcetype = fallback_cfg.get("sourcetype")

                if not index and not sourcetype:
                    continue

                target = {"device_id": device_id, "dataset_id": dataset_key}
                if index:
                    target["index"] = index
                if sourcetype:
                    target["sourcetype"] = sourcetype

                target_key = (target.get("index"), target.get("sourcetype"), device_id, dataset_key)
                if target_key in seen_targets:
                    continue
                seen_targets.add(target_key)
                resolved_targets.append(target)

        return resolved_targets

    def _device_matches_rule(self, device, rule_product: str) -> bool:
        """Return True when the tenant device is compatible with the rule product scope."""
        if rule_product in {"", "any", "generic", "unknown"}:
            return True

        device_product = self._normalize_value(device.product)
        device_vendor = self._normalize_value(device.vendor)
        return rule_product in {device_product, device_vendor}

    def _dataset_matches_rule(
        self,
        device,
        dataset: dict,
        rule_category: str,
        rule_service: str,
    ) -> bool:
        """Return True when one tenant dataset can satisfy the rule logsource scope."""
        dataset_category = self._normalize_value(dataset.get("category"))
        dataset_id = self._normalize_value(dataset.get("dataset_id"))
        dataset_service = self._normalize_value(dataset.get("service_id") or dataset.get("service"))
        dataset_type = self._normalize_value(dataset.get("log_type"))
        device_type = self._normalize_value(device.device_type)

        if rule_category not in {"", "any", "unknown"}:
            if rule_category not in {dataset_category, device_type}:
                return False

        if rule_service not in {"", "any", "unknown"}:
            if rule_service not in {dataset_id, dataset_service, dataset_type}:
                return False

        return True

    def _apply_query_targets(self, query: str, mapping: dict) -> str:
        """Apply resolved ingest targets to a hardcoded query string."""
        ingest_targets = mapping.get("ingest_targets") or []
        if ingest_targets:
            query = self._replace_pair_placeholders(query, ingest_targets)

        replacements = {
            "$INDEX$": mapping.get("index"),
            "$index$": mapping.get("index"),
            "$SOURCETYPE$": mapping.get("sourcetype"),
            "$sourcetype$": mapping.get("sourcetype"),
        }
        for placeholder, value in replacements.items():
            if isinstance(value, str):
                query = query.replace(placeholder, value)
        return query

    def _replace_pair_placeholders(self, query: str, ingest_targets: list[dict]) -> str:
        """Replace `index=$...$ sourcetype=$...$` pairs with concrete Splunk clauses."""
        pair_expression = self._build_ingest_expression(ingest_targets)
        if not pair_expression:
            return query

        pattern = re.compile(
            r"\(?\s*index\s*=\s*\$(?:INDEX|index)\$\s+"
            r"sourcetype\s*=\s*\$(?:SOURCETYPE|sourcetype)\$\s*\)?"
        )
        return pattern.sub(f"({pair_expression}) ", query, count=1).strip()

    def _build_ingest_expression(self, ingest_targets: list[dict]) -> str:
        """Build one Splunk OR clause from one or more concrete ingest targets."""
        clauses: list[str] = []
        for target in ingest_targets:
            index = target.get("index")
            sourcetype = target.get("sourcetype")
            if index and sourcetype:
                clauses.append(f"(index={index} sourcetype={sourcetype})")
            elif index:
                clauses.append(f"(index={index})")
            elif sourcetype:
                clauses.append(f"(sourcetype={sourcetype})")
        return " OR ".join(clauses)

    def _normalize_value(self, value: object) -> str:
        """Normalize repository strings so comparisons stay predictable."""
        if not isinstance(value, str):
            return ""
        return value.strip().lower().replace("-", "").replace("_", "").replace(" ", "")
