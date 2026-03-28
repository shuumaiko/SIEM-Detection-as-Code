---
name: project-root-code-maintainer
description: Maintain and modernize `project-root/` in this repository using the documented repository architecture as the source of business truth. Use when Codex needs to fix bugs, refactor outdated skeleton code, or add features inside `project-root/` while first defining business scope, mapping function flow, adding clear function-level comments or docstrings, and logging key implementation notes under `docs/note/logs/code/`.
---

# Project Root Code Maintainer

## Overview

Treat `docs/architecture/` and the repository data model as the business source of truth. Treat `project-root/` as a transitional Clean Architecture implementation that can contain thin pass-through layers and outdated assumptions.

Use this skill to keep code changes narrow, business-first, and auditable when working on the engine under `project-root/`.

## Quick Start

1. Read `docs/architecture/project-architecture.md`.
2. Read only the `project-root/` files on the affected path plus nearby tests in `project-root/tests/`.
3. Read [references/project-root-current-context.md](references/project-root-current-context.md) when you need the current flow map and layer heuristics.

## Required Guardrails

- Change code only inside `project-root/`.
- Allow one exception outside `project-root/`: create or update a task log under `docs/note/logs/code/`.
- Define the business scope before writing code.
- When adding or changing a function, add a clear docstring for purpose, important inputs, return shape, and side effects.
- Add inline comments only for non-obvious logic, branching, normalization, or side effects.
- Explain the function flow for every new capability before or alongside implementation.
- Prefer minimal edits that preserve current repository contracts unless the task explicitly requires broader refactoring.
- Do not rewrite repository-wide architecture from `project-root/` alone when docs and data contracts already define the intended model.

## Define Business Scope Before Code

Create a short business definition in your working notes, response, or task log before editing code. Include:

- Business goal
- User or operator outcome
- Entry command or trigger
- Main input data and output artifact
- Affected flow steps
- Correct ownership layer: `interfaces`, `app/usecases`, `app/services`, `domain`, or `infrastructure`
- Validation plan
- Log file path

If the requested behavior is ambiguous, resolve ambiguity by reading docs, current code, and tests first. Ask the user only when different choices would materially change repository behavior.

## Analyze Function Flow

For each new or changed capability, map the flow in this order:

1. Entry point: CLI or API function that receives the request.
2. Orchestration: use case that coordinates the scenario.
3. Business logic: service, builder, validator, or helper that transforms data.
4. Data access: repository, loader, or adapter that is touched.
5. Side effects: file write, schema validation, deployment call, or artifact output.
6. Failure points: missing file, invalid schema, mismatched IDs, or unsupported SIEM behavior.
7. Tests: smoke, unit, or targeted regression checks.

Capture this flow in the task log when the change is more than a tiny one-line fix.

## Place Logic In The Right Layer

- `interfaces/`: parse input, format output, choose the use case. Keep transport and presentation concerns here only.
- `app/usecases/`: coordinate one end-to-end scenario. Avoid filesystem details here.
- `app/services/`: hold reusable application logic shared by use cases.
- `domain/models` and `domain/repositories/`: represent business entities and ports without filesystem or vendor details.
- `infrastructure/...`: handle file parsing, repository persistence, registry loading, adapters, and compatibility with current on-disk structure.

When logic feels misplaced, move it only if the current task benefits from that change and you can cover it with tests. Do not refactor unrelated layers just because the skeleton is imperfect.

## Commenting Standard

For every new or modified function:

- Add or refresh a docstring that states purpose, important parameters, return shape, and major side effects.
- Add brief inline comments before non-obvious blocks such as normalization, fallback lookup, compatibility branches, or query mutation.
- Keep comments factual and maintainable. Do not narrate obvious assignments.

## Logging

Create or update a markdown log under `docs/note/logs/code/`. Use a dated filename such as `YYYY-MM-DD-<task-slug>.md`.

Include:

- Request summary
- Business definition
- Function flow summary
- Files changed
- Tests run
- Risks, follow-ups, or assumptions

## Verification

Prefer targeted verification close to the edited flow:

- existing tests under `project-root/tests/`
- a narrow `pytest` selection when possible
- manual CLI invocation only if safe and necessary

If you cannot run validation, state why in the log and final response.

## Current Context

Read [references/project-root-current-context.md](references/project-root-current-context.md) for the current flow map, known transitional patterns, and layer placement heuristics.
