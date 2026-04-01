# SIEM-Detection-as-Code Workspace Guide

This repository uses a layered Detection-as-Code model.
Treat this file as the top-level AI control contract for Codex and OMX sessions in this workspace.

## Source Of Truth

Use this priority order when deciding behavior:

1. `docs/architecture/`
2. `rules/`, `mappings/`, `execution/`, `tenants/`, `schema/`
3. `project-root/` as the current implementation
4. `artifacts/` only as generated output

Do not invent a parallel architecture when the repository docs already define one.

## Repository Model

- `rules/` stores reusable detection intent.
- `mappings/` stores field contracts and normalization.
- `execution/` stores SIEM execution policy and overrides.
- `tenants/` stores tenant-specific deployment context and bindings.
- `schema/` stores validation contracts.
- `project-root/` contains the engine that loads, validates, renders, exports, and deploys.
- `artifacts/` contains generated tenant output and is not a long-term manual editing surface.

## Working Rules

- Prefer changing `project-root/` or source data layers over hand-editing generated output.
- Do not treat `artifacts/` or generated deployment manifests as the primary source of truth.
- Do not treat `legacy/` folders as the default architecture unless the task explicitly targets legacy compatibility.
- Keep semantic rule content separate from SIEM-specific execution detail.
- Keep tenant-specific bindings and overrides inside the tenant layer.

## Skills

Repo-local skills live under `.codex/skills/`.
Use the relevant skill when the task clearly matches it, especially for:

- `siem-detection-as-code-base`
- `project-root-code-maintainer`
- `project-root-code-reviewer`
- `deployment-flow-reviewer`
- `detection-mapping-ocsf`
- `schema-fix-from-source`
- `tenant-config-from-siem-logs`
- `tenant-field-binding-writer`
- `tenant-onboard-from-siem-log`
- `merge-rule-into-base`

Read the skill's `SKILL.md` before following its workflow.

## Change Guidance

- Keep diffs small and architecture-aligned.
- Preserve existing repository conventions unless the task is explicitly a redesign.
- Add brief comments or docstrings only where the code would otherwise be hard to follow.
- When changing `project-root/`, prefer documenting important implementation notes under `log/YYYY-MM-DD/` when the active skill requires it.

## Verification

- Validate the narrowest relevant surface after changes.
- Prefer repository tests, validators, or command-level checks over assumptions.
- If you cannot run a verification step, say so clearly.

## OMX Integration

- `.codex/` is the AI control layer for this repository.
- `.omx/` is reserved for OMX runtime state, plans, logs, notepad, and HUD data.
- The vendored OMX source checkout lives under `.vendor/oh-my-codex/`.
- Launch OMX through `tools/omx-safe.ps1` so `CODEX_HOME` resolves to `.codex/`.
- Prefer `omx setup --scope user` through the wrapper so OMX writes prompts, agents, config, and AGENTS into `.codex/` instead of the workspace root.
- Do not use `omx setup --scope project` unless you intentionally want OMX to create or manage a root-level `AGENTS.md`.
