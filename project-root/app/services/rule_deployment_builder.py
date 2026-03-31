import re

from infrastructure.file_loader.detection_field_mapping_loader import DetectionFieldMappingLoader
from infrastructure.file_loader.registry_loader import RegistryLoader
from infrastructure.file_loader.tenant_filter_override_loader import TenantFilterOverrideLoader


class RuleDeploymentBuilder:
    """Resolve ingest targets and build deployment payloads for rendered rules."""

    _QUERY_RESERVED_TOKENS = {
        "and",
        "as",
        "avg",
        "bin",
        "bucket",
        "by",
        "case",
        "cidrmatch",
        "coalesce",
        "convert",
        "count",
        "ctime",
        "dc",
        "earliest",
        "eval",
        "false",
        "fields",
        "fillnull",
        "if",
        "in",
        "latest",
        "like",
        "lower",
        "max",
        "min",
        "mvindex",
        "mvjoin",
        "not",
        "null",
        "or",
        "rename",
        "rex",
        "search",
        "sort",
        "span",
        "stats",
        "sum",
        "table",
        "true",
        "upper",
        "value",
        "values",
        "where",
    }

    def __init__(
        self,
        registry_loader: RegistryLoader,
        detection_field_mapping_loader: DetectionFieldMappingLoader | None = None,
        tenant_filter_override_loader: TenantFilterOverrideLoader | None = None,
    ) -> None:
        """Store loaders used for ingest target resolution and query field mapping."""
        self.registry_loader = registry_loader
        self.detection_field_mapping_loader = detection_field_mapping_loader
        self.tenant_filter_override_loader = tenant_filter_override_loader

    def build(self, tenant, exported_rules: list[dict]) -> tuple[list[dict], dict]:
        """Return rendered rule payloads with resolved targets plus one deployment manifest.

        Parameters:
            tenant: Active tenant whose ingest bindings should be applied.
            exported_rules: Flat source rule payloads ready for target resolution.

        Returns:
            A tuple of `(mapped_rules, payload)` where `mapped_rules` contains one
            rendered rule per deployable ingest target, and `payload` is the
            tenant deployment manifest document.
        """
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

            # Apply tenant query tuning before field rewriting so override queries
            # can still use source-rule field names and flow through the normal
            # source -> canonical -> tenant field translation.
            self._apply_tenant_filter_override(tenant, mapped)
            mapping = self._resolve_mapping(tenant, mapped)
            # Drop rules that do not resolve to any deployable ingest target so
            # the hardcoded-query flow cannot emit empty artifacts or manifest entries.
            if not mapping:
                continue
            expanded_mappings = self._expand_mappings(mapping)
            for expanded_mapping in expanded_mappings:
                rendered_rule = dict(mapped)
                rendered_rule["source_rule_id"] = rule_id
                rendered_rule = self._apply_mapping(rendered_rule, expanded_mapping)
                rendered_rule["id"] = self._build_rendered_rule_id(
                    source_rule_id=rule_id,
                    mapping=expanded_mapping,
                )
                rendered_rule["artifact_suffix"] = self._build_artifact_suffix(expanded_mapping)
                mapped_rules.append(rendered_rule)
                rendered_rule_id = rendered_rule.get("id") or rule_id
                deployments.append(
                    {
                        "rule_id": rendered_rule_id,
                        "enabled": existing_enabled_by_rule_id.get(rendered_rule_id, True),
                        "display_name": rendered_rule.get("display_name") or rendered_rule_id,
                    }
                )

        payload = {
            "schema_version": 1.0,
            "tenant_id": tenant.tenant_id,
            "rule_deployments_by_siem": {tenant.siem_id or "": deployments},
        }
        return mapped_rules, payload

    def _apply_tenant_filter_override(self, tenant, item: dict) -> None:
        """Replace one hardcoded query with a tenant filter override when present.

        Parameters:
            tenant: Active tenant whose `overrides/filter/` tree may contain a rule override.
            item: Flat render payload that still uses source-rule field names in its query.

        Side effects:
            Updates `item["search_query"]` in place when a tenant filter override
            provides `query_modifiers.<siem>.search_query` for the current rule.
        """
        if self.tenant_filter_override_loader is None:
            return

        rule_id = item.get("id")
        if not isinstance(rule_id, str) or not rule_id:
            return

        override_query = self.tenant_filter_override_loader.load_query_override(
            tenant_id=getattr(tenant, "tenant_id", ""),
            siem_id=getattr(tenant, "siem_id", "") or "",
            rule_id=rule_id,
            rule_name=item.get("source_rule_name"),
        )
        if override_query:
            item["search_query"] = override_query

    def _expand_mappings(self, mapping: dict) -> list[dict]:
        """Split one resolved mapping into per-target variants when needed.

        Parameters:
            mapping: Resolved ingest target mapping for one source rule.

        Returns:
            A list of mappings. Rules with exactly one ingest target stay as one
            mapping, while rules that match multiple tenant logsources expand into
            one mapping per ingest target so each rendered rule has an unambiguous
            device and dataset. Empty or invalid mappings return an empty list.
        """
        ingest_targets = mapping.get("ingest_targets") or []
        if not isinstance(ingest_targets, list) or not ingest_targets:
            return []
        if len(ingest_targets) == 1:
            return [mapping]

        expanded: list[dict] = []
        for target in ingest_targets:
            if not isinstance(target, dict):
                continue
            expanded.append(
                {
                    "ingest_targets": [target],
                    "index": target.get("index"),
                    "sourcetype": target.get("sourcetype"),
                    "_is_split_variant": True,
                }
            )
        return expanded or [mapping]

    def _resolve_mapping(self, tenant, item: dict) -> dict:
        """Resolve the effective ingest targets for one rendered rule candidate."""
        targets = item.get("targets") or {}
        if self._has_explicit_targets(targets):
            return self._resolve_explicit_targets(tenant, item, targets)

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
        """Apply resolved ingest targets to the flat rendered-rule payload.

        Parameters:
            item: Flat source rule payload being rendered.
            mapping: One resolved target mapping, which may already be narrowed to
                a single ingest target variant.

        Returns:
            The rendered rule payload with direct target fields, prefixed display
            name, and final query text.
        """
        if not mapping:
            return item

        targets = dict(item.get("targets") or {})
        ingest_targets = mapping.get("ingest_targets") or []
        if ingest_targets:
            # Preserve the fully expanded target list for rules that map to multiple datasets.
            targets["ingest_targets"] = [
                self._sanitize_target_for_output(target)
                for target in ingest_targets
                if isinstance(target, dict)
            ]
            if len(ingest_targets) == 1 and isinstance(ingest_targets[0], dict):
                single_target = ingest_targets[0]
                for key in ("device_id", "dataset_id", "index", "sourcetype"):
                    value = single_target.get(key)
                    if isinstance(value, str) and value:
                        targets[key] = value

        index = mapping.get("index")
        sourcetype = mapping.get("sourcetype")
        if index and not targets.get("index"):
            targets["index"] = index
        if sourcetype and not targets.get("sourcetype"):
            targets["sourcetype"] = sourcetype
        item["targets"] = targets
        item["display_name"] = self._prefix_with_device_id(
            item.get("display_name") or item.get("id"),
            targets,
        )

        query = item.get("search_query")
        field_bindings = {}
        if len(ingest_targets) == 1 and isinstance(ingest_targets[0], dict):
            candidate_bindings = ingest_targets[0].get("_field_bindings")
            if isinstance(candidate_bindings, dict):
                field_bindings = {
                    str(key).lower(): value
                    for key, value in candidate_bindings.items()
                    if isinstance(key, str) and isinstance(value, str) and value.strip()
                }
        if isinstance(query, str):
            query = self._apply_query_targets(query, mapping, field_bindings)
            item["search_query"] = query
        return item

    def _build_rendered_rule_id(self, source_rule_id: str, mapping: dict) -> str:
        """Return the deployment identifier for one rendered rule variant.

        Parameters:
            source_rule_id: Original semantic source rule identifier.
            mapping: One resolved target mapping, potentially representing a split variant.

        Returns:
            The original source rule ID for single-target rules, or a target-scoped
            identifier when one source rule expands into multiple deployable rules.
        """
        if not mapping.get("_is_split_variant"):
            return source_rule_id

        ingest_targets = mapping.get("ingest_targets") or []
        if not isinstance(ingest_targets, list) or len(ingest_targets) != 1:
            return source_rule_id

        target = ingest_targets[0]
        if not isinstance(target, dict):
            return source_rule_id

        device_id = str(target.get("device_id") or "unknown-device")
        dataset_id = str(target.get("dataset_id") or "unknown-dataset")
        return f"{source_rule_id}::{device_id}::{dataset_id}"

    def _build_artifact_suffix(self, mapping: dict) -> str | None:
        """Return a filename suffix for split rendered rule variants.

        Parameters:
            mapping: One resolved target mapping.

        Returns:
            A filesystem-safe suffix such as `__device__dataset` for split variants,
            or `None` when the source rule stays as one artifact.
        """
        if not mapping.get("_is_split_variant"):
            return None

        ingest_targets = mapping.get("ingest_targets") or []
        if not isinstance(ingest_targets, list) or len(ingest_targets) != 1:
            return None

        target = ingest_targets[0]
        if not isinstance(target, dict):
            return None

        device_id = self._sanitize_artifact_component(target.get("device_id"))
        dataset_id = self._sanitize_artifact_component(target.get("dataset_id"))
        if not device_id:
            return None
        if dataset_id:
            return f"__{device_id}__{dataset_id}"
        return f"__{device_id}"

    def _sanitize_artifact_component(self, value: object) -> str:
        """Normalize one artifact filename component derived from target metadata."""
        if not isinstance(value, str):
            return ""
        return re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-")

    def _sanitize_target_for_output(self, target: dict) -> dict:
        """Return one target payload without internal render-only metadata."""
        return {
            key: value
            for key, value in target.items()
            if not str(key).startswith("_")
        }

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

    def _resolve_explicit_targets(self, tenant, item: dict, targets: dict) -> dict:
        """Normalize explicit targets and attach query field bindings when possible."""
        normalized = self._normalize_existing_targets(targets)
        ingest_targets = normalized.get("ingest_targets")
        if not isinstance(ingest_targets, list) or not ingest_targets:
            direct_target = {
                key: normalized.get(key)
                for key in ("device_id", "dataset_id", "index", "sourcetype")
                if isinstance(normalized.get(key), str) and normalized.get(key)
            }
            ingest_targets = [direct_target] if direct_target else []

        enriched_targets: list[dict] = []
        for target in ingest_targets:
            if not isinstance(target, dict):
                continue
            enriched_target = self._attach_target_field_bindings(tenant, item, target)
            if enriched_target is not None:
                enriched_targets.append(enriched_target)

        if not enriched_targets:
            return {}

        mapping: dict = {"ingest_targets": enriched_targets}
        indexes = sorted({target["index"] for target in enriched_targets if target.get("index")})
        sourcetypes = sorted(
            {target["sourcetype"] for target in enriched_targets if target.get("sourcetype")}
        )
        if len(indexes) == 1:
            mapping["index"] = indexes[0]
        if len(sourcetypes) == 1:
            mapping["sourcetype"] = sourcetypes[0]
        return mapping

    def _collect_ingest_targets(self, tenant, item: dict) -> list[dict]:
        """Collect tenant ingest bindings whose device and dataset match one source rule.

        Parameters:
            tenant: Active tenant whose devices, logsources, and bindings are queried.
            item: Flat source rule payload whose logsource scope is being resolved.

        Returns:
            Concrete ingest targets that satisfy the rule scope and also expose an
            actual tenant field mapping. This prevents generating artifacts for
            datasets that only have ingest wiring but no proven field contract.
        """
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

                enriched_target = self._attach_target_field_bindings(tenant, item, target)
                if enriched_target is None:
                    continue

                target_key = (
                    enriched_target.get("index"),
                    enriched_target.get("sourcetype"),
                    device_id,
                    dataset_key,
                )
                if target_key in seen_targets:
                    continue
                seen_targets.add(target_key)
                resolved_targets.append(enriched_target)

        return resolved_targets

    def _attach_target_field_bindings(self, tenant, item: dict, target: dict) -> dict | None:
        """Attach tenant field bindings for one concrete target or reject the target.

        Parameters:
            tenant: Active tenant whose bindings are being queried.
            item: Flat source rule payload whose query is being rendered.
            target: Concrete ingest target candidate with `device_id` and `dataset_id`.

        Returns:
            The same target plus `_field_bindings` when the query can be mapped to
            tenant fields, or `None` when the target lacks the required contract.
        """
        device_id = target.get("device_id")
        dataset_key = target.get("dataset_id")
        if not isinstance(device_id, str) or not device_id:
            return None
        if not isinstance(dataset_key, str) or not dataset_key:
            return None

        binding = tenant.bindings.get(device_id)
        if binding is None:
            return None

        field_bindings = self._resolve_query_field_bindings(item, binding, dataset_key)
        if field_bindings is None:
            return None

        enriched_target = dict(target)
        if field_bindings:
            enriched_target["_field_bindings"] = field_bindings
        return enriched_target

    def _resolve_query_field_bindings(
        self,
        item: dict,
        binding,
        dataset_key: str,
    ) -> dict[str, str] | None:
        """Return source-query-field to tenant-field bindings for one target dataset.

        Parameters:
            item: Flat source rule payload whose hardcoded query is being rendered.
            binding: Tenant binding object for the target device.
            dataset_key: Dataset identifier currently being evaluated.

        Returns:
            A lowercase source-field alias map valued by concrete tenant SIEM field
            names, or `None` when the query cannot be rendered through the
            `source -> canonical -> tenant` field-mapping chain.
        """
        query = item.get("search_query")
        if not isinstance(query, str) or not query.strip():
            return {}
        if self.detection_field_mapping_loader is None:
            return None

        source_to_canonical = self.detection_field_mapping_loader.resolve_source_to_canonical_fields(
            category=item.get("category"),
            product=item.get("product"),
            service=item.get("service"),
            source_path=item.get("source_path"),
        )
        if not source_to_canonical:
            return None

        dataset_field_mapping = self._resolve_dataset_field_mapping(binding, dataset_key)
        if not dataset_field_mapping:
            return None

        source_to_tenant = {
            source_field: dataset_field_mapping[canonical_field]
            for source_field, canonical_field in source_to_canonical.items()
            if isinstance(dataset_field_mapping.get(canonical_field), str)
            and dataset_field_mapping.get(canonical_field).strip()
        }

        rule_fields = {
            value.strip().lower()
            for value in item.get("fields") or []
            if isinstance(value, str) and value.strip()
        }
        if not self._validate_query_field_bindings(
            query=query,
            source_to_canonical=source_to_canonical,
            source_to_tenant=source_to_tenant,
            rule_fields=rule_fields,
        ):
            return None

        return source_to_tenant

    def _resolve_dataset_field_mapping(self, binding, dataset_key: str) -> dict[str, str]:
        """Return the concrete canonical-to-tenant field map for one device dataset."""
        field_mappings = getattr(binding, "field_mappings", {}) or {}
        dataset_mapping = field_mappings.get(dataset_key)
        if isinstance(dataset_mapping, dict) and dataset_mapping:
            return {
                key: value.strip()
                for key, value in dataset_mapping.items()
                if isinstance(key, str) and isinstance(value, str) and value.strip()
            }

        default_mapping = field_mappings.get("_default")
        if isinstance(default_mapping, dict) and default_mapping:
            return {
                key: value.strip()
                for key, value in default_mapping.items()
                if isinstance(key, str) and isinstance(value, str) and value.strip()
            }

        return {}

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

    def _apply_query_targets(self, query: str, mapping: dict, field_bindings: dict[str, str]) -> str:
        """Apply resolved ingest targets to and normalize a hardcoded query string.

        Parameters:
            query: Source hardcoded query before tenant ingest resolution.
            mapping: Resolved ingest target information for the current tenant rule.

        Returns:
            A query string with ingest placeholders replaced and redundant blank
            lines removed so rendered artifacts stay readable.
        """
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
        if field_bindings:
            query = self._apply_field_bindings_to_query(query, field_bindings)
        return self._normalize_query_whitespace(query)

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

    def _normalize_query_whitespace(self, query: str) -> str:
        """Collapse redundant blank lines and trailing spaces in rendered queries.

        Parameters:
            query: Query string after ingest placeholder substitution.

        Returns:
            The cleaned query with line content preserved, trailing whitespace
            removed, and multiple empty lines collapsed to a single line break.
        """
        normalized_lines = [line.rstrip() for line in query.replace("\r\n", "\n").split("\n")]
        cleaned_lines: list[str] = []
        previous_blank = False

        # Preserve the query's multiline structure while removing the extra
        # empty lines introduced by placeholder replacement and YAML source layout.
        for line in normalized_lines:
            is_blank = line == ""
            if is_blank and previous_blank:
                continue
            cleaned_lines.append(line)
            previous_blank = is_blank

        return "\n".join(cleaned_lines).strip()

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

    def _validate_query_field_bindings(
        self,
        *,
        query: str,
        source_to_canonical: dict[str, str],
        source_to_tenant: dict[str, str],
        rule_fields: set[str],
    ) -> bool:
        """Return True when every query field can traverse the two mapping layers."""
        derived_aliases: set[str] = set()
        previous_token_lower: str | None = None
        position = 0

        while position < len(query):
            char = query[position]
            if char in {'"', "'"}:
                _, position = self._read_quoted_segment(query, position)
                continue
            if not self._is_token_start(char):
                position += 1
                continue

            token, position = self._read_token(query, position)
            token_lower = token.lower()
            next_nonspace = self._peek_next_nonspace_char(query, position)

            if previous_token_lower == "as":
                derived_aliases.add(token_lower)
            elif token_lower in derived_aliases:
                pass
            elif token_lower in self._QUERY_RESERVED_TOKENS:
                pass
            elif next_nonspace == "(" and token_lower not in source_to_canonical:
                pass
            elif token_lower in source_to_canonical:
                if token_lower not in source_to_tenant:
                    return False
            elif token_lower in rule_fields:
                return False

            previous_token_lower = token_lower

        return True

    def _apply_field_bindings_to_query(self, query: str, field_bindings: dict[str, str]) -> str:
        """Rewrite source-rule field tokens in one query to tenant SIEM field names."""
        rewritten: list[str] = []
        derived_aliases: set[str] = set()
        previous_token_lower: str | None = None
        position = 0

        while position < len(query):
            char = query[position]
            if char in {'"', "'"}:
                quoted_segment, position = self._read_quoted_segment(query, position)
                rewritten.append(quoted_segment)
                continue
            if not self._is_token_start(char):
                rewritten.append(char)
                position += 1
                continue

            token, position = self._read_token(query, position)
            token_lower = token.lower()
            next_nonspace = self._peek_next_nonspace_char(query, position)

            if previous_token_lower == "as":
                derived_aliases.add(token_lower)
                rewritten.append(token)
            elif token_lower in derived_aliases:
                rewritten.append(token)
            elif token_lower in self._QUERY_RESERVED_TOKENS:
                rewritten.append(token)
            elif next_nonspace == "(" and token_lower not in field_bindings:
                rewritten.append(token)
            else:
                rewritten.append(field_bindings.get(token_lower, token))

            previous_token_lower = token_lower

        return "".join(rewritten)

    def _read_quoted_segment(self, query: str, start_index: int) -> tuple[str, int]:
        """Return one quoted query segment unchanged, preserving escaped characters."""
        quote_char = query[start_index]
        position = start_index + 1
        while position < len(query):
            current_char = query[position]
            if current_char == "\\":
                position += 2
                continue
            if current_char == quote_char:
                position += 1
                break
            position += 1
        return query[start_index:position], position

    def _read_token(self, query: str, start_index: int) -> tuple[str, int]:
        """Read one identifier-like token from a Splunk query string."""
        position = start_index
        while position < len(query) and self._is_token_character(query[position]):
            position += 1
        return query[start_index:position], position

    def _peek_next_nonspace_char(self, query: str, start_index: int) -> str:
        """Return the next non-space character after one token, or an empty string."""
        position = start_index
        while position < len(query) and query[position].isspace():
            position += 1
        if position >= len(query):
            return ""
        return query[position]

    def _is_token_start(self, value: str) -> bool:
        """Return True when one character can start a field or command token."""
        return value.isalpha() or value == "_"

    def _is_token_character(self, value: str) -> bool:
        """Return True when one character can belong to a field-like token."""
        return value.isalnum() or value in {"_", ".", "-"}

    def _prefix_with_device_id(self, display_name: object, targets: dict) -> str:
        """Prefix one deployment display name with device_id when one target device is resolved."""
        base_name = str(display_name)
        device_id = self._resolve_single_device_id(targets)
        if not device_id:
            return base_name
        prefix = f"{device_id} - "
        if base_name.startswith(prefix):
            return base_name
        return f"{prefix}{base_name}"

    def _resolve_single_device_id(self, targets: dict) -> str | None:
        """Return one device_id when the resolved target set points to a single tenant device."""
        direct_device_id = targets.get("device_id")
        if isinstance(direct_device_id, str) and direct_device_id.strip():
            return direct_device_id.strip()

        ingest_targets = targets.get("ingest_targets")
        if not isinstance(ingest_targets, list):
            return None

        device_ids = {
            item.get("device_id").strip()
            for item in ingest_targets
            if isinstance(item, dict)
            and isinstance(item.get("device_id"), str)
            and item.get("device_id").strip()
        }
        if len(device_ids) == 1:
            return next(iter(device_ids))
        return None
