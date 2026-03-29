import json
from datetime import date, datetime
from pathlib import Path

import jsonschema
import yaml


def _load_schema() -> dict:
    schema_path = Path(__file__).resolve().parents[1] / "schema" / "rules" / "base_rule.schema.json"
    return json.loads(schema_path.read_text(encoding="utf-8-sig"))


def _load_rule(relative_path: str) -> dict:
    rule_path = Path(__file__).resolve().parents[1] / relative_path
    return _normalize_dates(yaml.safe_load(rule_path.read_text(encoding="utf-8")))


def _normalize_dates(value):
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: _normalize_dates(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize_dates(item) for item in value]
    return value


def test_av_detection_rule_matches_tightened_detection_schema() -> None:
    schema = _load_schema()
    rule = _load_rule("rules/detections/category/antivirus/av_webshell.yml")

    jsonschema.validate(instance=rule, schema=schema)


def test_base_rule_can_omit_fields_and_x_query() -> None:
    schema = _load_schema()
    rule = _load_rule("rules/detections/network/firewall/base/fw_external_connection.yaml")

    jsonschema.validate(instance=rule, schema=schema)


def test_detection_rule_without_rule_type_is_rejected() -> None:
    schema = _load_schema()
    rule = _load_rule("rules/detections/network/firewall/net_firewall_cleartext_protocols.yml")
    rule.pop("rule_type")

    try:
        jsonschema.validate(instance=rule, schema=schema)
    except jsonschema.ValidationError:
        return

    raise AssertionError("Expected schema validation to reject detection rule without rule_type.")


def test_detection_rule_without_required_detection_fields_is_rejected() -> None:
    schema = _load_schema()
    rule = _load_rule("rules/detections/category/antivirus/av_relevant_files.yml")
    rule.pop("fields")
    rule.pop("x_query")

    try:
        jsonschema.validate(instance=rule, schema=schema)
    except jsonschema.ValidationError:
        return

    raise AssertionError("Expected schema validation to reject detection rule without fields/x_query.")
