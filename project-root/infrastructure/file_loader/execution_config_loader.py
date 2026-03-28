from __future__ import annotations

from pathlib import Path
from typing import Any

from infrastructure.file_loader.yaml_loader import YamlLoader


class ExecutionConfigLoader:
    """Load and merge effective execution metadata for one tenant rule render."""

    def __init__(self, execution_root: str | Path, tenants_root: str | Path) -> None:
        """Store shared execution and tenant override roots."""
        self.execution_root = Path(execution_root)
        self.tenants_root = Path(tenants_root)
        self.yaml_loader = YamlLoader()

    def load_effective_config(
        self,
        tenant_id: str,
        siem_id: str,
        rule_id: str,
        rule_name: str | None = None,
        rule_level: str | None = None,
    ) -> dict:
        """Return merged execution config from defaults, rule overrides, and tenant overrides."""
        effective: dict[str, Any] = {}
        if not siem_id:
            return effective

        defaults_doc = self._load_yaml(self.execution_root / siem_id / "defaults.yaml")
        if defaults_doc:
            self._merge_nested_dicts(effective, self._select_default_config(defaults_doc, rule_level))

        overrides_doc = self._load_yaml(self.execution_root / siem_id / "rule-overrides.yaml")
        rules_by_id = overrides_doc.get("rules_by_id") if isinstance(overrides_doc, dict) else {}
        if isinstance(rules_by_id, dict):
            self._merge_nested_dicts(
                effective,
                self._filter_execution_fields(rules_by_id.get(rule_id)),
            )

        tenant_override = self._load_tenant_override(tenant_id, siem_id, rule_id, rule_name)
        self._merge_nested_dicts(effective, tenant_override)
        return effective

    def _select_default_config(self, defaults_doc: dict, rule_level: str | None) -> dict:
        """Select default execution values, including level-specific notable tuning."""
        selected: dict[str, Any] = {}
        self._merge_nested_dicts(selected, defaults_doc.get("defaults") or {})

        level_defaults = defaults_doc.get("level_defaults") or {}
        if isinstance(level_defaults, dict) and isinstance(rule_level, str):
            self._merge_nested_dicts(
                selected,
                self._filter_execution_fields(level_defaults.get(rule_level.lower())),
            )
        return selected

    def _load_tenant_override(
        self,
        tenant_id: str,
        siem_id: str,
        rule_id: str,
        rule_name: str | None,
    ) -> dict:
        """Return the tenant-specific execution override for one rule when it exists."""
        tenant_execution_root = self.tenants_root / tenant_id / "overrides" / "execution" / siem_id
        if not tenant_execution_root.exists():
            return {}

        for pattern in ("*.execution.yaml", "*.execution.yml"):
            for path in sorted(tenant_execution_root.rglob(pattern)):
                data = self._load_yaml(path)
                if not isinstance(data, dict):
                    continue
                if data.get("rule_id") == rule_id:
                    return self._filter_execution_fields(data)
                if rule_name and data.get("rule_name") == rule_name:
                    return self._filter_execution_fields(data)
        return {}

    def _filter_execution_fields(self, data: object) -> dict:
        """Keep only execution fields that belong in the rendered artifact."""
        if not isinstance(data, dict):
            return {}

        filtered: dict[str, Any] = {}
        for key in ("enabled", "display_name", "schedule", "notable"):
            value = data.get(key)
            if value is not None:
                filtered[key] = value
        return filtered

    def _merge_nested_dicts(self, base: dict, incoming: dict) -> None:
        """Recursively merge nested execution dictionaries in override order."""
        for key, value in incoming.items():
            if isinstance(value, dict) and isinstance(base.get(key), dict):
                self._merge_nested_dicts(base[key], value)
                continue
            base[key] = value

    def _load_yaml(self, path: Path) -> dict:
        """Load one YAML file when present, otherwise return an empty dictionary."""
        if not path.exists():
            return {}
        try:
            data = self.yaml_loader.load(path)
        except Exception:
            return {}
        return data if isinstance(data, dict) else {}
