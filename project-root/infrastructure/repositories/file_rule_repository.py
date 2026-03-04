from pathlib import Path

from domain.models.rule import Rule
from domain.repositories.rule_repository import RuleRepository
from infrastructure.file_loader.yaml_loader import YamlLoader


class FileRuleRepository(RuleRepository):
    """File-backed rule repository implementation."""

    def __init__(self, base_path: str) -> None:
        """Create repository with rules root directory."""
        self.base_path = Path(base_path)
        self.loader = YamlLoader()

    def list_by_category(self, category: str) -> list[Rule]:
        """List rules under one detection category."""
        category_path = self.base_path / "detection" / category
        return self._scan_rules(category_path)

    def list_for_tenant(self, tenant_id: str) -> list[Rule]:
        """List rules applicable for tenant (placeholder strategy)."""
        # Placeholder strategy: return all detection rules for now.
        detection_path = self.base_path / "detection"
        return self._scan_rules(detection_path)

    def _scan_rules(self, root: Path) -> list[Rule]:
        """Recursively load rule files from a directory."""
        if not root.exists():
            return []

        result: list[Rule] = []
        for path in root.rglob("*.yml"):
            data = self.loader.load(path)
            result.append(
                Rule(
                    rule_id=data.get("id", path.stem),
                    category=data.get("category", "unknown"),
                    product=data.get("product"),
                    raw=data,
                )
            )

        for path in root.rglob("*.yaml"):
            if path.suffix.lower() != ".yaml":
                continue
            data = self.loader.load(path)
            result.append(
                Rule(
                    rule_id=data.get("id", path.stem),
                    category=data.get("category", "unknown"),
                    product=data.get("product"),
                    raw=data,
                )
            )

        return result
