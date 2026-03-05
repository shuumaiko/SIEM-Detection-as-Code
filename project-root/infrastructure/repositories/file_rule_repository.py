from pathlib import Path

from domain.models.rule import Rule
from domain.models.tenant import Tenant
from domain.repositories.rule_repository import RuleRepository
from infrastructure.file_loader.yaml_loader import YamlLoader


class FileRuleRepository(RuleRepository):
    """File-backed rule repository implementation."""

    def __init__(self, base_path: str | Path, tenant_rules_path: str | Path) -> None:
        self.base_path = Path(base_path)
        self.tenant_rules_path = Path(tenant_rules_path)
        self.loader = YamlLoader()

    def list_by_category(self, category: str) -> list[Rule]:
        category_path = self.base_path / "detection" / category
        return self._scan_base_rules(category_path)

    def list_for_tenant(self, tenant: Tenant) -> list[Rule]:
        tenant_root = self.tenant_rules_path / tenant.tenant_id
        if not tenant_root.exists():
            return []

        enabled_rule_ids = tenant.enabled_rule_ids()
        result: list[Rule] = []
        for path in sorted(list(tenant_root.rglob("*.yml")) + list(tenant_root.rglob("*.yaml"))):
            try:
                data = self.loader.load(path)
            except Exception:
                continue
            if not isinstance(data, dict):
                continue

            rule_id = data.get("id", path.stem)
            if enabled_rule_ids and rule_id not in enabled_rule_ids:
                continue

            siem_ext = data.get("x_splunk_es", {}) if tenant.siem_id == "splunk" else {}
            logsource = data.get("logsource", {})
            result.append(
                Rule(
                    rule_id=rule_id,
                    category=logsource.get("category", data.get("category", "unknown")),
                    product=logsource.get("product", data.get("product")),
                    siem_query=siem_ext.get("search_query"),
                    siem_targets=siem_ext.get("targets"),
                    raw=data,
                )
            )
        return result

    def _scan_base_rules(self, root: Path) -> list[Rule]:
        if not root.exists():
            return []

        result: list[Rule] = []
        for path in sorted(list(root.rglob("*.yml")) + list(root.rglob("*.yaml"))):
            try:
                data = self.loader.load(path)
            except Exception:
                continue
            if not isinstance(data, dict):
                continue
            result.append(
                Rule(
                    rule_id=data.get("id", path.stem),
                    category=data.get("category", "unknown"),
                    product=data.get("product"),
                    raw=data,
                )
            )
        return result
