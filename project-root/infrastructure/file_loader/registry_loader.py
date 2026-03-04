from pathlib import Path

from infrastructure.file_loader.yaml_loader import YamlLoader


class RegistryLoader:
    """Load logsource registry documents from file system."""

    def __init__(self, root: str | Path) -> None:
        """Create loader with registry root path."""
        self.root = Path(root)
        self.yaml_loader = YamlLoader()

    def load_vendor_registry(self, vendor: str, product: str) -> dict:
        """Load one vendor/product registry mapping."""
        # Convention: registry file path can be customized later.
        file_path = self.root / vendor / product / "mapping.yaml"
        if not file_path.exists():
            return {}
        return self.yaml_loader.load(file_path)
