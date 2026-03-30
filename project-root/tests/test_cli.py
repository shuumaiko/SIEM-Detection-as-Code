import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from interfaces.cli import run_cli


def test_validate_rules_cli_prints_pretty_json(capsys) -> None:
    """Validate that rule validation output is emitted as readable JSON."""

    class StubUseCase:
        def execute(self, since=None, validate_all=False):
            return {
                "valid": False,
                "mode": "all" if validate_all else "since",
                "since": since,
                "summary": {"errors": 1, "warnings": 0},
                "errors": ["example"],
                "warnings": [],
            }

    def build_app():
        stub = object()
        return stub, stub, stub, stub, StubUseCase()

    run_cli(build_app_fn=build_app, argv=["validate-rules", "--all"])

    output = capsys.readouterr().out
    parsed = json.loads(output)
    assert parsed["valid"] is False
    assert parsed["summary"]["errors"] == 1
    assert output.startswith("{\n  ")
