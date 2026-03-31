from pathlib import Path
import shutil

import yaml

from app.services.rule_format_validator import RuleFormatValidator


def test_validate_rules_rejects_analyst_without_logsource() -> None:
    workspace_root = Path(__file__).resolve().parents[2]
    test_root = workspace_root / "project-root" / ".tmp-tests" / "rule-format-validator"
    if test_root.exists():
        shutil.rmtree(test_root)
    test_root.mkdir(parents=True, exist_ok=True)

    rules_root = test_root / "rules"
    analyst_rule_path = rules_root / "analysts" / "review" / "analyst_missing_logsource.yaml"
    analyst_rule_path.parent.mkdir(parents=True, exist_ok=True)

    with open(analyst_rule_path, "w", encoding="utf-8") as file:
        yaml.safe_dump(
            {
                "title": "Review analyst missing logsource",
                "id": "11111111-2222-3333-4444-555555555555",
                "rule_type": "analyst",
                "status": "stable",
                "description": "Review analyst rule without explicit logsource.",
                "references": ["internal-review"],
                "author": "OpenAI",
                "date": "2026-03-31",
                "tags": ["review"],
                "correlation": {
                    "type": "event_count",
                    "rules": ["fw_external_connection"],
                    "group-by": ["src_ip"],
                    "timespan": "1h",
                    "condition": {"gt": 0},
                },
                "fields": ["src_ip", "count"],
                "falsepositives": ["Expected review fixture traffic"],
                "level": "low",
                "x_query": {
                    "splunk": "index=$index$ sourcetype=$sourcetype$ | stats count by src_ip"
                },
            },
            file,
            sort_keys=False,
            allow_unicode=True,
            width=4096,
        )

    validator = RuleFormatValidator(
        rules_root=rules_root,
        schemas_root=workspace_root / "schema" / "rules",
    )

    result = validator.validate(validate_all=True)

    assert result["valid"] is False
    assert any(
        "analyst rules must declare logsource.category, logsource.product, and logsource.service."
        in error
        for error in result["errors"]
    )
