from pathlib import Path

from infrastructure.file_loader.yaml_loader import YamlLoader


class RegistryLoader:
    """Load logsource-registry documents from file system."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.yaml_loader = YamlLoader()

    def resolve_siem_config(self, vendor: str | None, product: str | None, siem_id: str) -> dict:
        if not vendor or not siem_id:
            return {}

        vendor_norm = self._normalize(vendor)
        product_norm = self._normalize(product or "")
        vendor_root = self.root / "vendor" / vendor_norm
        if not vendor_root.exists():
            return {}

        conf_files = list(vendor_root.rglob(f"*{siem_id}*conf*.y*ml"))
        if not conf_files and product_norm:
            conf_files = [
                path for path in vendor_root.rglob("*conf*.y*ml") if product_norm in self._normalize(path.stem)
            ]
        for path in sorted(conf_files):
            try:
                data = self.yaml_loader.load(path)
            except Exception:
                continue
            if isinstance(data, dict) and isinstance(data.get("config"), dict):
                return data["config"]
        return {}

    def _normalize(self, value: str) -> str:
        return value.strip().lower().replace(" ", "").replace("-", "").replace("_", "")
