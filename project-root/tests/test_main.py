import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import main


def test_main_exits_with_dependency_install_hint_when_module_is_missing(monkeypatch) -> None:
    """Ensure startup import errors become actionable operator guidance."""

    def stub_run_cli(*, build_app_fn, argv=None) -> None:
        del build_app_fn, argv
        raise ModuleNotFoundError("No module named 'yaml'", name="yaml")

    monkeypatch.setattr(main, "run_cli", stub_run_cli)

    try:
        main.main(["validate-rules", "--all"])
    except SystemExit as exc:
        message = str(exc)
    else:
        raise AssertionError("Expected SystemExit when a required module is missing.")

    assert "Missing Python module 'yaml'" in message
    assert "requirements.txt" in message
    assert "-m pip install -r" in message
