from __future__ import annotations

from pathlib import Path

from infrastructure.file_loader.yaml_loader import YamlLoader


class TenantFilterOverrideLoader:
    """Load tenant filter overrides that can replace one hardcoded SIEM query."""

    def __init__(self, tenants_root: str | Path) -> None:
        """Store the tenant root that contains `overrides/filter/` documents."""
        self.tenants_root = Path(tenants_root)
        self.yaml_loader = YamlLoader()

    def load_query_override(
        self,
        tenant_id: str,
        siem_id: str,
        rule_id: str,
        rule_name: str | None = None,
    ) -> str | None:
        """Return one tenant-specific query override for a rendered rule when present.

        Parameters:
            tenant_id: Tenant whose override tree should be searched.
            siem_id: Active SIEM identifier used to select one query modifier branch.
            rule_id: Stable rule identifier used as the primary override key.
            rule_name: Optional semantic rule name used as a fallback lookup key.

        Returns:
            A hardcoded query string from `query_modifiers.<siem>.search_query`, or
            `None` when no matching filter override exists for the rule.
        """
        if not tenant_id or not siem_id or not rule_id:
            return None

        filter_root = self.tenants_root / tenant_id / "overrides" / "filter"
        if not filter_root.exists():
            return None

        by_rule_name: list[dict] = []
        for path in sorted(list(filter_root.rglob("*.filter.yaml")) + list(filter_root.rglob("*.filter.yml"))):
            data = self._load_yaml(path)
            if not isinstance(data, dict):
                continue
            if data.get("rule_id") == rule_id:
                return self._extract_search_query(data, siem_id)
            if rule_name and data.get("rule_name") == rule_name:
                by_rule_name.append(data)

        for data in by_rule_name:
            query = self._extract_search_query(data, siem_id)
            if query:
                return query
        return None

    def _extract_search_query(self, data: dict, siem_id: str) -> str | None:
        """Return one SIEM-specific override query from a filter override document."""
        query_modifiers = data.get("query_modifiers") or {}
        if not isinstance(query_modifiers, dict):
            return None

        siem_modifier = query_modifiers.get(siem_id) or {}
        if not isinstance(siem_modifier, dict):
            return None

        search_query = siem_modifier.get("search_query")
        if not isinstance(search_query, str) or not search_query.strip():
            return None
        return search_query.strip()

    def _load_yaml(self, path: Path) -> dict:
        """Load one YAML document and normalize unreadable files to an empty dict."""
        if not path.exists():
            return {}
        try:
            data = self.yaml_loader.load(path)
        except Exception:
            return {}
        return data if isinstance(data, dict) else {}
