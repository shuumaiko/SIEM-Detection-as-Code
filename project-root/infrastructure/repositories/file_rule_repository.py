import shutil
from pathlib import Path

import yaml

from domain.models.rule import Rule
from domain.models.tenant import Tenant
from domain.repositories.rule_repository import RuleRepository
from infrastructure.file_loader.yaml_loader import YamlLoader


class FileRuleRepository(RuleRepository):
    """File-backed rule repository implementation."""

    def __init__(self, base_path: str | Path, tenant_rules_path: str | Path) -> None:
        """Store base-rule root and artifact root used by the render pipeline."""
        self.base_path = Path(base_path)
        self.tenant_rules_path = Path(tenant_rules_path)
        self.loader = YamlLoader()

    def list_by_category(self, category: str) -> list[Rule]:
        """Read base rules from one category under the active rules root."""
        category_path = self._resolve_rules_root() / category
        return self._scan_base_rules(category_path)

    def list_for_tenant(self, tenant: Tenant, include_all: bool = False) -> list[Rule]:
        """Read already-rendered tenant rules from the artifact layer."""
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
                    source_path=str(path.relative_to(tenant_root)),
                    raw=data,
                )
            )
        return result

    def list_render_candidates(self, tenant: Tenant) -> list[Rule]:
        """Read source detection rules that expose a hardcoded query for the tenant SIEM."""
        rules_root = self._resolve_rules_root()
        result: list[Rule] = []
        for path in sorted(list(rules_root.rglob("*.yml")) + list(rules_root.rglob("*.yaml"))):
            try:
                data = self.loader.load(path)
            except Exception:
                continue
            if not isinstance(data, dict):
                continue

            siem_query, siem_targets = self._extract_siem_config(data, tenant.siem_id or "")
            if not siem_query:
                continue

            logsource = data.get("logsource", {})
            result.append(
                Rule(
                    rule_id=data.get("id", path.stem),
                    category=logsource.get("category", data.get("category", "unknown")),
                    product=logsource.get("product", data.get("product")),
                    siem_query=siem_query,
                    siem_targets=siem_targets,
                    source_path=str(path.relative_to(rules_root)),
                    raw=data,
                )
            )
        return result

    def save_rendered_for_tenant(self, tenant_id: str, rendered_rules: list[dict]) -> None:
        """Write rendered tenant rules under `artifacts/<tenant>/tenant-rules/detections`."""
        target_root = self.tenant_rules_path / tenant_id / "tenant-rules" / "detections"
        if target_root.exists():
            shutil.rmtree(target_root)

        for item in rendered_rules:
            relative_path = Path(str(item.get("relative_path") or ""))
            if relative_path.is_absolute() or ".." in relative_path.parts:
                continue

            document = item.get("document")
            if not isinstance(document, dict):
                continue

            output_path = target_root / relative_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as file:
                yaml.safe_dump(document, file, sort_keys=False, allow_unicode=True, width=4096)

    def _resolve_rules_root(self) -> Path:
        """Return the active detection rules root while supporting old folder names."""
        candidates = (
            self.base_path / "detections",
            self.base_path / "detection",
        )
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return candidates[0]

    def _resolve_tenant_rules_root(self, tenant_id: str) -> Path | None:
        """Return the tenant artifact root while supporting legacy artifact layouts."""
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

    def _extract_siem_config(self, data: dict, siem_id: str) -> tuple[str | None, dict]:
        """Extract the source hardcoded query and any pre-existing SIEM targets."""
        x_query = data.get("x_query") or {}
        if isinstance(x_query, dict):
            query = x_query.get(siem_id)
            if isinstance(query, str) and query.strip():
                return query, {}

        if siem_id == "splunk":
            x_splunk_es = data.get("x_splunk_es") or {}
            if isinstance(x_splunk_es, dict):
                query = x_splunk_es.get("search_query")
                if isinstance(query, str) and query.strip():
                    targets = x_splunk_es.get("targets") or {}
                    return query, targets if isinstance(targets, dict) else {}

        return None, {}
