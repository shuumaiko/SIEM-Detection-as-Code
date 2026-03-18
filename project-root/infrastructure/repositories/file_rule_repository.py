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
        category_path = self._resolve_rules_root() / category
        return self._scan_base_rules(category_path)

    def list_for_tenant(self, tenant: Tenant, include_all: bool = False) -> list[Rule]:
        tenant_root = self._resolve_tenant_rules_root(tenant.tenant_id)
        if tenant_root is None:
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
            if not include_all and enabled_rule_ids and rule_id not in enabled_rule_ids:
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

    def _resolve_rules_root(self) -> Path:
        candidates = (
            self.base_path / "detections",
            self.base_path / "detection",
        )
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return candidates[0]

    def _resolve_tenant_rules_root(self, tenant_id: str) -> Path | None:
        candidates = (
            self.tenant_rules_path / tenant_id / "tenant-rules" / "detections",
            self.tenant_rules_path / tenant_id / "tenant-rules" / "detection-raw",
            self.tenant_rules_path / tenant_id,
        )
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return None

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
