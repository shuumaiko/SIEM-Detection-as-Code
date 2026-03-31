---
name: project-root-code-reviewer
description: Review `project-root/` behavior and implementation in this repository using the documented repository architecture as the business source of truth. Use when Codex needs to inspect code, rerun commands, validate behavior, compare generated outputs, or test the project without modifying source files, while logging findings under `log/YYYY-MM-DD/project-root-code-reviewer/`.
---

# Project Root Code Reviewer

## Overview

Treat `docs/architecture/` and the repository data model as the business source of truth.

Base the review lens on `$project-root-code-maintainer`, but do review work only. Reuse the same flow-mapping discipline and architecture reading, while replacing implementation work with evidence gathering, reruns, tests, and findings.

Use this skill to review behavior in `project-root/` without modifying source files.

## Quick Start

1. Read `docs/architecture/project-architecture.md`.
2. Read the `project-root/` files under review and the closest tests in `project-root/tests/`.
3. Read `../project-root-code-maintainer/references/project-root-current-context.md` when you need the current flow map and layer heuristics.
4. Inspect the current diff or current repository state before running commands so you know what changed and what must not be overwritten.

## Required Guardrails

- Do not edit source files during the review.
- Treat these paths as source files for this skill: `project-root/`, `rules/`, `mappings/`, `tenants/`, `schema/`, `artifacts/`, `docs/`, and `.codex/skills/`.
- Allow one intentional write target: create or update a markdown log under `log/YYYY-MM-DD/project-root-code-reviewer/`.
- Allow normal side effects from rerun or test commands only when those side effects are necessary to observe behavior, such as temporary output under `.tmp-tests/` or generated artifacts produced by the command under review.
- Do not "fix while reviewing." Report findings instead.
- Do not revert, clean, or overwrite generated diffs produced by rerun or test commands unless the user explicitly asks.
- If a rerun or test mutates tracked files, treat that as review evidence and describe it clearly.

## Define Review Scope Before Commands

Capture a short review definition in your working notes, response, or review log before running the heavier checks. Include:

- Review goal
- Suspected risk or user concern
- Entry command or workflow being reviewed
- Main files or layers inspected
- Validation or rerun plan
- Log file path

## Analyze Function Flow

Map the behavior in this order before judging whether it is correct:

1. Entry point: CLI or API function that receives the request.
2. Orchestration: use case that coordinates the scenario.
3. Business logic: service, builder, validator, or helper that transforms data.
4. Data access: repository, loader, or adapter that is touched.
5. Side effects: file write, schema validation, deployment call, or artifact output.
6. Failure points: missing file, invalid schema, mismatched IDs, or unsupported SIEM behavior.
7. Tests or reruns: focused checks that can confirm the behavior.

## Review Workflow

Follow this order.

1. Read the minimal architecture, code, and test context needed for the target review.
2. Identify the exact flow and risk being checked.
3. Inspect changed files or behavior-driving files before running commands.
4. Run the smallest useful validation, rerun, or test that can confirm the suspected behavior.
5. Compare the observed behavior against architecture docs, schemas, tests, and current repository contracts.
6. Record findings with severity, evidence, and impact.
7. Stop after review. Do not patch source files as part of this skill.

## Allowed Verification Work

- Run focused `pytest` selections under `project-root/tests/`.
- Run narrow CLI validation such as `python project-root/main.py validate-tenant --tenant-id <tenant>` when tenant behavior is under review.
- Run `python project-root/main.py validate-rules --all` when rule validation behavior is part of the review and the broader run is justified.
- Re-run safe project commands when the review depends on observing rendered output, generated artifacts, or current CLI behavior.
- Compare newly generated output with existing repository output when that comparison is the evidence needed for the review.
- Prefer the smallest command that proves or disproves the concern.

## Review Focus

Prioritize findings in this order:

- bugs or behavioral regressions
- contract drift against docs, schemas, or repository data shape
- missing validation or test coverage near the changed flow
- operational risks, hidden side effects, or ambiguous ownership boundaries

Keep summaries brief. Put findings first.

## Logging

Create or update a markdown log under `log/YYYY-MM-DD/project-root-code-reviewer/`.

- Use the current local date for `YYYY-MM-DD`.
- Use a short filename such as `<task-slug>.md`.
- Include the request summary, review scope, files inspected, commands run, findings, supporting evidence, generated outputs touched by reruns, and any assumptions.
- State explicitly that the review did not modify source files.

## Output Contract

When using this skill, report in this order:

1. Findings, ordered by severity, with file and line references when possible.
2. Open questions or assumptions.
3. Verification summary with commands run or skipped.

If no findings are discovered, say that explicitly and mention any residual risk or unrun checks.

## Completion Checklist

Before finishing, verify all of the following.

- No source file was edited during the review.
- The review log path is recorded.
- Every finding is backed by code, command, or output evidence.
- Any rerun or test side effects are described.
- Any validation you could not run is stated clearly.
