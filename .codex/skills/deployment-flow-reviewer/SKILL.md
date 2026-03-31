---
name: deployment-flow-reviewer
description: Test and review the real deployment flow in this repository from rules and tenant inputs through validation, artifact generation, deployment manifests, and deploy-ready output. Use when Codex needs to rerun deployment-related commands, inspect rendered artifacts or deployment manifests, verify real tenant enablement and target resolution, or determine whether a deployment issue comes from repository data or `project-root/` code. If the suspected root cause is inside `project-root/`, explicitly use `project-root-code-reviewer` to investigate the code path.
---

# Deployment Flow Reviewer

## Overview

Use this skill to review the end-to-end deployment flow that turns repository source data into deploy-ready tenant output.

Treat the real deployment chain as:

`rules/ -> mappings/ -> tenants/ -> project-root CLI or use case -> deployments/rule-deployments.yaml -> artifacts/ -> deploy-ready output`

This is a review and test skill, not a fix skill. Re-run commands, inspect outputs, compare source-of-truth layers, and classify the root cause. Do not patch source files as part of this skill.

## Quick Start

1. Read `docs/architecture/project-architecture.md`.
2. Read `docs/architecture/rule-rendering-flows.md`.
3. Read `docs/architecture/tenants-relationship.md`.
4. Read the specific tenant, rule, mapping, artifact, and deployment files involved in the reported scenario.
5. Read `project-root/interfaces/cli.py` and the closest tests in `project-root/tests/` when the review depends on observed command behavior.

## Required Guardrails

- Do not edit source files during the review.
- Treat these paths as source files for this skill: `rules/`, `mappings/`, `tenants/`, `schema/`, `project-root/`, `artifacts/`, `docs/`, and `.codex/skills/`.
- Allow one intentional write target: create or update a markdown log under `log/YYYY-MM-DD/deployment-flow-reviewer/`.
- Allow normal side effects from rerun or test commands only when those side effects are needed to observe behavior, such as `.tmp-tests/` output, refreshed artifacts, or regenerated tenant deployment manifests.
- Prefer copied workspaces or existing `.tmp-tests/` patterns when a rerun would otherwise overwrite tracked outputs.
- Do not hand-edit generated artifacts or `deployments/rule-deployments.yaml` during the review.
- If the likely root cause is in `project-root/` code or cannot be isolated without code-path analysis, explicitly invoke `$project-root-code-reviewer`.

## Define The Review Scenario

Capture a short scenario definition in your working notes, response, or review log before running the heavier checks. Include:

- Tenant and `siem_id` under review
- Entry command or workflow being tested
- Expected artifact, manifest, or deployment behavior
- Source files or layers that seem most relevant
- Validation or rerun plan
- Log file path

## Source-Of-Truth Chain

Trace the scenario in this order.

1. `rules/`: reusable detection or analyst content that should be deployable.
2. `mappings/`: canonical field contracts required by the rules.
3. `tenants/`: device, dataset, ingest, field binding, filter, override, and deployment inputs for the tenant.
4. `project-root/`: CLI entrypoint and use case or service path that reads the repository state.
5. `tenants/<tenant>/deployments/rule-deployments.yaml`: final tenant enablement decision when the flow writes or refreshes it.
6. `artifacts/`: rendered deploy-ready output or evidence of what the pipeline produced.
7. Adapter or deployment result: the final summary returned by `deploy-rules` or the equivalent current flow.

## Review Workflow

Follow this order.

1. Identify the exact deployment scenario and the expected output.
2. Read the minimal source-of-truth chain needed to understand that scenario.
3. Inspect the current artifact or deployment manifest state before rerunning commands.
4. Run the smallest useful validation, render, export, or deploy command that can confirm the observed behavior.
5. Compare the observed output against rules, mappings, tenant config, deployment decisions, and architecture docs.
6. Classify the issue as one of:
   - source data or config issue
   - artifact or deployment-state issue
   - `project-root/` code-path issue
   - unresolved and needs deeper code review
7. If the issue is code-related or still ambiguous after the data-layer review, invoke `$project-root-code-reviewer` with the exact command, tenant, files, and observed symptoms.
8. Record findings, evidence, and next action. Do not patch source files in this skill.

## Allowed Verification Work

- Run `python project-root/main.py validate-tenant --tenant-id <tenant>`.
- Run `python project-root/main.py validate-rules --all` when broad rule validation is justified.
- Run `python project-root/main.py gen-artifact --tenant-id <tenant>` or `python project-root/main.py export-rules --tenant-id <tenant>` when the review depends on rendered output and summary metadata.
- Run `python project-root/main.py deploy-rules --tenant-id <tenant>` only when the current adapter behavior is safe to observe for this repository state.
- Run focused tests such as `project-root/tests/test_export_rules.py`, `project-root/tests/test_rule_deployment_builder.py`, `project-root/tests/test_cli.py`, or `project-root/tests/test_smoke.py` when they are the narrowest confirmation path.
- Compare rerun output against existing `artifacts/` and tenant deployment manifests when that comparison is the evidence needed.

## Escalate To Code Review

Invoke `$project-root-code-reviewer` when any of these are true:

- the source files look consistent but the CLI or use case output is still wrong
- a deployment manifest or artifact is written with the wrong IDs, targets, enabled state, or query content
- the failure appears after entering `project-root/` rather than in `rules/`, `mappings/`, or `tenants/`
- the review needs root-cause analysis inside `app/usecases/`, `app/services/`, `infrastructure/`, or CLI wiring

When invoking `$project-root-code-reviewer`, pass:

- the exact command or test that reproduced the issue
- the tenant and SIEM context
- the source files already checked
- the observed artifact or manifest mismatch

## Review Focus

Prioritize findings in this order:

- wrong rule enablement or target resolution
- drift between tenant inputs and generated deployment state
- rendered artifact mismatches against the expected source-of-truth chain
- missing validation or regression coverage for deployment behavior
- code-path suspicion that needs `project-root-code-reviewer`

Put findings first. Keep the narrative short.

## Logging

Create or update a markdown log under `log/YYYY-MM-DD/deployment-flow-reviewer/`.

- Use the current local date for `YYYY-MM-DD`.
- Use a short filename such as `<task-slug>.md`.
- Include the request summary, review scenario, commands run, source files inspected, findings, artifact or manifest evidence, root-cause classification, whether `$project-root-code-reviewer` was invoked, and any assumptions.
- State explicitly that this review did not modify source files.

## Output Contract

When using this skill, report in this order:

1. Findings, ordered by severity, with file or artifact references when possible.
2. Root-cause classification: data or config, deployment-state, code-path, or unresolved.
3. Verification summary with commands run or skipped.
4. Whether `$project-root-code-reviewer` was used or should be used next.

If no findings are discovered, say that explicitly and mention any residual risk or unrun checks.

## Completion Checklist

Before finishing, verify all of the following.

- No source file was edited during the review.
- The source-of-truth chain was checked only as deeply as needed.
- Every finding is backed by code, command, artifact, or deployment-manifest evidence.
- Any rerun or test side effects are described.
- Any escalation to `$project-root-code-reviewer` is explicit.
