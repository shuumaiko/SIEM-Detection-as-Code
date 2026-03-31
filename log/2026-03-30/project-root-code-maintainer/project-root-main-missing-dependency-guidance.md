# Request Summary

- Check the startup error captured in `main-bug.txt` when running `project-root/main.py`.

# Business Definition

- Business goal: make the CLI fail with a clear operator-facing dependency message instead of a raw traceback when required Python modules are missing.
- User or operator outcome: the person running `project-root/main.py` can immediately see which module is missing and the install command for the active interpreter.
- Entry command or trigger: `python project-root/main.py ...`
- Main input data and output artifact: startup import errors in the CLI bootstrap; stderr `SystemExit` message with dependency guidance.
- Affected flow steps: entry point bootstrap, dependency wiring handoff to `interfaces.cli.run_cli`, missing-module failure handling.
- Correct ownership layer: `project-root/main.py` entrypoint bootstrap and `project-root/tests/` regression coverage.
- Validation plan: run targeted pytest coverage for `project-root/tests/test_main.py` and smoke tests if the environment supports them.
- Log file path: `log/2026-03-30/project-root-code-maintainer/project-root-main-missing-dependency-guidance.md`

# Function Flow Summary

1. `main.main()` remains the CLI entry point.
2. `interfaces.cli.run_cli()` still owns argument parsing and dispatch.
3. `build_app()` now performs lazy imports so the bootstrap can catch missing dependency failures closer to the entry point.
4. When a module import fails, `_format_missing_dependency_error()` builds a message that includes the missing module and a pip install command against the current interpreter.
5. `main.main()` raises `SystemExit` with that guidance instead of surfacing the raw traceback alone.

# Files Changed

- `project-root/main.py`
- `project-root/tests/test_main.py`
- `log/2026-03-30/project-root-code-maintainer/project-root-main-missing-dependency-guidance.md`

# Tests Run

- `python -m pytest project-root/tests/test_main.py project-root/tests/test_smoke.py`
- `python project-root/main.py -h`
- `d:\Personal\SIEM-Detection-as-Code\.venv.py312-broken-backup\Scripts\python.exe d:\Personal\SIEM-Detection-as-Code\project-root\main.py validate-rules --all`

# Risks And Follow-Ups

- This change improves failure guidance but does not install dependencies automatically; the runtime environment still needs `PyYAML` and any other required packages.
- If future startup failures come from missing internal modules rather than third-party packages, the message still stays truthful by calling them “missing Python modules” and only suggesting dependency installation conditionally.

