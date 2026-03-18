from pathlib import Path

import yaml


class YamlLoader:
    """Thin YAML loader utility for local file-backed repositories."""

    def load(self, file_path: str | Path) -> dict:
        """Load one YAML/YML file into a dictionary."""
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
