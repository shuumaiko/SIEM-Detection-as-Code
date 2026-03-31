# Code Log: Create `project-root-code-maintainer` Skill

## Request Summary

Create a reusable skill based on the current `project-root/` context so future code changes stay business-first, limited to `project-root/`, clearly commented, flow-aware, and logged under `log/YYYY-MM-DD/project-root-code-maintainer/`.

## Context Reviewed

- `docs/architecture/project-architecture.md`
- `README.md`
- `project-root/main.py`
- `project-root/interfaces/cli.py`
- `project-root/app/usecases/*.py` on the main command paths
- `project-root/app/services/*.py` on export, deploy, validation, and tenant loading
- `project-root/infrastructure/repositories/file_tenant_repository.py`
- `project-root/infrastructure/repositories/file_rule_repository.py`
- `project-root/tests/test_smoke.py`
- `project-root/tests/test_folder_architecture.py`
- `project-root/tests/test_rule_deployment_builder.py`
- `project-root/tests/test_validate_tenant_config.py`

## Business Definition

- Goal: create a skill that guides safe maintenance and modernization of `project-root/`.
- Outcome: future tasks define business scope first, place logic in the correct layer, comment touched functions clearly, analyze flow before implementing new behavior, and keep an audit log.
- Trigger: any bug fix, refactor, or new feature request that touches `project-root/`.
- Primary inputs: architecture docs, `project-root/` source files, and nearby tests.
- Primary outputs: updated code under `project-root/` and a dated task log under `log/YYYY-MM-DD/project-root-code-maintainer/`.

## Key Decisions

- Use `docs/architecture/project-architecture.md` as the business source of truth when `project-root/` still reflects legacy or transitional assumptions.
- Limit code edits to `project-root/`, with one explicit exception for task logs under `log/YYYY-MM-DD/project-root-code-maintainer/`.
- Encode a mandatory "business definition before code" step in the skill instead of relying on ad hoc reasoning.
- Keep the skill lean and place the current flow map in a separate reference file so the main `SKILL.md` stays readable.

## Files Created

- `docs/skills/project-root-code-maintainer/SKILL.md`
- `docs/skills/project-root-code-maintainer/references/project-root-current-context.md`
- `docs/skills/project-root-code-maintainer/agents/openai.yaml`
- `log/2026-03-28/project-root-code-maintainer/project-root-code-maintainer-skill.md`

## Validation Notes

- `init_skill.py` was used to initialize the skill folder.
- The first initialization pass failed when generating `agents/openai.yaml` because the initial `short_description` exceeded the allowed UI length.
- The skill content and `agents/openai.yaml` were then completed manually with valid metadata.

## Assumptions And Risks

- The user instruction "only change files in `project-root/`" is interpreted as applying to code changes; the log requirement under `log/YYYY-MM-DD/project-root-code-maintainer/` is treated as an intentional exception.
- No `project-root/` source code was changed in this task.

