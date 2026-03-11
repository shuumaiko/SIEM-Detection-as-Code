from infrastructure.file_loader.registry_loader import RegistryLoader


class RuleDeploymentBuilder:
    """Build rule-deployments payload and mapped export items."""

    def __init__(self, registry_loader: RegistryLoader) -> None:
        self.registry_loader = registry_loader

    def build(self, tenant, exported_rules: list[dict]) -> tuple[list[dict], dict]:
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
        targets = item.get("targets") or {}
        current_index = targets.get("index")
        current_sourcetype = targets.get("sourcetype")
        if current_index and current_sourcetype:
            return {"index": current_index, "sourcetype": current_sourcetype}

        dataset = item.get("dataset") or item.get("service")
        category = item.get("category")
        for device_id, device in tenant.devices.items():
            if device.device_type and category and device.device_type != category:
                continue
            logsource = tenant.logsources.get(device_id)
            if not logsource:
                continue
            datasets = logsource.datasets or []
            if dataset and not any(svc.get("dataset_id") == dataset or svc.get("service_id") == dataset for svc in datasets):
                continue

            binding = tenant.bindings.get(device_id)
            if binding:
                bind_cfg = binding.bindings.get(dataset, {})
                if bind_cfg.get("index") or bind_cfg.get("sourcetype"):
                    return {
                        "index": bind_cfg.get("index"),
                        "sourcetype": bind_cfg.get("sourcetype"),
                    }

            return self.registry_loader.resolve_siem_config(
                vendor=device.vendor,
                product=device.product,
                siem_id=tenant.siem_id or "",
            )
        return {}

    def _apply_mapping(self, item: dict, mapping: dict) -> dict:
        if not mapping:
            return item

        targets = dict(item.get("targets") or {})
        index = mapping.get("index")
        sourcetype = mapping.get("sourcetype")
        if index and not targets.get("index"):
            targets["index"] = index
        if sourcetype and not targets.get("sourcetype"):
            targets["sourcetype"] = sourcetype
        item["targets"] = targets

        query = item.get("search_query")
        if isinstance(query, str):
            if index:
                query = query.replace("$INDEX$", str(index))
            if sourcetype:
                query = query.replace("$SOURCETYPE$", str(sourcetype))
            item["search_query"] = query
        return item
