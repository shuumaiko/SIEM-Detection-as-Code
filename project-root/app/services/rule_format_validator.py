from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml


class RuleFormatValidator:
    """Validate detection rule file format against rule schemas."""

    def __init__(self, rules_root: str | Path, schemas_root: str | Path) -> None:
        self.rules_root = Path(rules_root)
        self.schemas_root = Path(schemas_root)

    def validate(self, since: str | None = None, validate_all: bool = False) -> dict:
        errors: list[str] = []
        warnings: list[str] = []
        files_scanned = 0
        files_selected = 0

        mode = "all" if validate_all else "since"
        since_date: date | None = None
        if not validate_all:
            if not since:
                return self._result(
                    mode=mode,
                    since=since,
                    files_scanned=0,
                    files_selected=0,
                    rules_checked=0,
                    errors=["Missing required filter: provide --all or --since dd/mm/yyyy."],
                    warnings=[],
                )
            try:
                since_date = datetime.strptime(since, "%d/%m/%Y").date()
            except ValueError:
                return self._result(
                    mode=mode,
                    since=since,
                    files_scanned=0,
                    files_selected=0,
                    rules_checked=0,
                    errors=[f"Invalid --since date '{since}'. Expected format: dd/mm/yyyy."],
                    warnings=[],
                )

        validator = self._build_schema_validator()
        if validator is None:
            warnings.append("jsonschema is not installed; schema validation is skipped.")

        base_schema = self._load_json(self.schemas_root / "base_rule.schema.json", errors)
        corr_schema = self._load_json(self.schemas_root / "correlation_rule.schema.json", errors)
        if base_schema is None or corr_schema is None:
            return self._result(
                mode=mode,
                since=since,
                files_scanned=0,
                files_selected=0,
                rules_checked=0,
                errors=errors,
                warnings=warnings,
            )

        detection_root = self._resolve_detection_root()
        if not detection_root.exists():
            errors.append(f"Detection rules directory not found: {detection_root}")
            return self._result(
                mode=mode,
                since=since,
                files_scanned=0,
                files_selected=0,
                rules_checked=0,
                errors=errors,
                warnings=warnings,
            )

        rule_files = sorted(list(detection_root.rglob("*.yml")) + list(detection_root.rglob("*.yaml")))

        for file_path in rule_files:
            files_scanned += 1
            docs = self._load_yaml_docs(file_path, errors)
            if docs is None:
                continue

            if len(docs) != 2:
                errors.append(
                    f"{file_path}: expected 2 YAML documents (base + correlation), got {len(docs)}."
                )
                continue

            base_doc, corr_doc = docs[0], docs[1]

            if not isinstance(base_doc, dict):
                errors.append(f"{file_path}: document #1 (base rule) must be an object.")
                continue
            if not isinstance(corr_doc, dict):
                errors.append(f"{file_path}: document #2 (correlation rule) must be an object.")
                continue

            if since_date is not None:
                rule_date = self._extract_rule_date(base_doc)
                if rule_date is None:
                    warnings.append(
                        f"{file_path}: cannot read 'modified'/'date' for --since filter; file skipped."
                    )
                    continue
                if rule_date < since_date:
                    continue

            files_selected += 1
            normalized_base = self._normalize_dates(base_doc)

            self._validate_schema(base_schema, normalized_base, validator, file_path, "#1", errors)
            self._validate_schema(corr_schema, corr_doc, validator, file_path, "#2", errors)

        return self._result(
            mode=mode,
            since=since,
            files_scanned=files_scanned,
            files_selected=files_selected,
            rules_checked=files_selected,
            errors=errors,
            warnings=warnings,
        )

    def _result(
        self,
        mode: str,
        since: str | None,
        files_scanned: int,
        files_selected: int,
        rules_checked: int,
        errors: list[str],
        warnings: list[str],
    ) -> dict:
        return {
            "valid": len(errors) == 0,
            "mode": mode,
            "since": since,
            "summary": {
                "files_scanned": files_scanned,
                "files_selected": files_selected,
                "rules_checked": rules_checked,
                "errors": len(errors),
                "warnings": len(warnings),
            },
            "errors": errors,
            "warnings": warnings,
        }

    def _build_schema_validator(self) -> Any | None:
        try:
            import jsonschema  # type: ignore
        except ModuleNotFoundError:
            return None
        return jsonschema

    def _load_yaml_docs(self, path: Path, errors: list[str]) -> list[Any] | None:
        try:
            with open(path, "r", encoding="utf-8") as file:
                return list(yaml.safe_load_all(file))
        except Exception as exc:
            errors.append(f"{path}: failed to parse YAML: {exc}")
            return None

    def _load_json(self, path: Path, errors: list[str]) -> dict | None:
        import json

        if not path.exists():
            errors.append(f"Schema not found: {path}")
            return None

        try:
            with open(path, "r", encoding="utf-8-sig") as file:
                return json.load(file)
        except Exception as exc:
            errors.append(f"Failed to load schema {path}: {exc}")
            return None

    def _validate_schema(
        self,
        schema: dict,
        data: Any,
        validator: Any | None,
        file_path: Path,
        doc_label: str,
        errors: list[str],
    ) -> None:
        if validator is None:
            return
        try:
            validator.validate(instance=data, schema=schema)
        except Exception as exc:
            errors.append(f"{file_path} document {doc_label}: schema validation error: {exc}")

    def _extract_rule_date(self, base_doc: dict[str, Any]) -> date | None:
        value = base_doc.get("modified")
        parsed = self._parse_date(value)
        if parsed is not None:
            return parsed

        value = base_doc.get("date")
        return self._parse_date(value)

    def _parse_date(self, value: Any) -> date | None:
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
        return None

    def _normalize_dates(self, base_doc: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(base_doc)
        for key in ("date", "modified"):
            value = normalized.get(key)
            if isinstance(value, datetime):
                normalized[key] = value.date().isoformat()
            elif isinstance(value, date):
                normalized[key] = value.isoformat()
        return normalized

    def _resolve_detection_root(self) -> Path:
        candidates = (
            self.rules_root / "detections",
            self.rules_root / "detection",
        )
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return candidates[0]
