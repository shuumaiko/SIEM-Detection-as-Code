from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml


class RuleFormatValidator:
    """Validate rule file format against repository rule schemas."""

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

        detection_schema = self._load_json(self.schemas_root / "base_rule.schema.json", errors)
        analyst_schema = self._load_json(self.schemas_root / "correlation_rule.schema.json", errors)
        if detection_schema is None or analyst_schema is None:
            return self._result(
                mode=mode,
                since=since,
                files_scanned=0,
                files_selected=0,
                rules_checked=0,
                errors=errors,
                warnings=warnings,
            )

        rule_files = self._collect_rule_files()
        if not rule_files:
            errors.append(f"Rule directories not found under: {self.rules_root}")
            return self._result(
                mode=mode,
                since=since,
                files_scanned=0,
                files_selected=0,
                rules_checked=0,
                errors=errors,
                warnings=warnings,
            )

        for file_path in rule_files:
            files_scanned += 1
            doc = self._load_yaml_doc(file_path, errors)
            if doc is None:
                continue
            if not isinstance(doc, dict):
                errors.append(f"{file_path}: rule file must contain a single YAML object.")
                continue

            if since_date is not None:
                rule_date = self._extract_rule_date(doc)
                if rule_date is None:
                    warnings.append(
                        f"{file_path}: cannot read 'modified'/'date' for --since filter; file skipped."
                    )
                    continue
                if rule_date < since_date:
                    continue

            files_selected += 1
            normalized_doc = self._normalize_dates(doc)
            schema = self._select_schema(normalized_doc, detection_schema, analyst_schema)
            if schema is None:
                errors.append(
                    f"{file_path}: unsupported or missing rule_type '{normalized_doc.get('rule_type')}'."
                )
                continue

            self._validate_schema(schema, normalized_doc, validator, file_path, errors)

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

    def _load_yaml_doc(self, path: Path, errors: list[str]) -> dict[str, Any] | None:
        try:
            with open(path, "r", encoding="utf-8") as file:
                docs = list(yaml.safe_load_all(file))
        except Exception as exc:
            errors.append(f"{path}: failed to parse YAML: {exc}")
            return None

        if len(docs) != 1:
            errors.append(f"{path}: expected 1 YAML document, got {len(docs)}.")
            return None

        return docs[0]

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
        errors: list[str],
    ) -> None:
        if validator is None:
            return
        try:
            validator.validate(instance=data, schema=schema)
        except Exception as exc:
            errors.append(f"{file_path}: schema validation error: {exc}")

    def _extract_rule_date(self, doc: dict[str, Any]) -> date | None:
        value = doc.get("modified")
        parsed = self._parse_date(value)
        if parsed is not None:
            return parsed

        value = doc.get("date")
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

    def _normalize_dates(self, doc: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(doc)
        for key in ("date", "modified"):
            value = normalized.get(key)
            if isinstance(value, datetime):
                normalized[key] = value.date().isoformat()
            elif isinstance(value, date):
                normalized[key] = value.isoformat()
        return normalized

    def _collect_rule_files(self) -> list[Path]:
        roots = []
        detection_root = self.rules_root / "detections"
        analysts_root = self.rules_root / "analysts"
        if detection_root.exists():
            roots.append(detection_root)
        if analysts_root.exists():
            roots.append(analysts_root)

        rule_files: list[Path] = []
        for root in roots:
            rule_files.extend(sorted(list(root.rglob("*.yml")) + list(root.rglob("*.yaml"))))
        return sorted(rule_files)

    def _select_schema(
        self,
        doc: dict[str, Any],
        detection_schema: dict,
        analyst_schema: dict,
    ) -> dict | None:
        rule_type = doc.get("rule_type")
        if rule_type in {"detection", "detection_base", "base"}:
            return detection_schema
        if rule_type == "analyst":
            return analyst_schema

        if "detection" in doc:
            return detection_schema
        if "correlation" in doc:
            return analyst_schema
        return None
