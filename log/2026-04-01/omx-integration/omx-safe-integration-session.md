# Request Summary

- Integrate `oh-my-codex` into this repository safely.
- Keep the AI control layer under `.codex/`.
- Keep OMX runtime state under `.omx/`.
- Avoid letting OMX take over or overwrite the repository's existing project-local skills blindly.
- Save the outcome of this work as a session log.

# Business Definition

- Business goal: enable OMX to be used in this repository without breaking the repository's existing Codex skill model.
- User or operator outcome: the repository can use OMX as a runtime and workflow layer while preserving `.codex/` as the highest AI control layer.
- Main integration rule: `.codex/` owns AI control surfaces; `.omx/` owns OMX runtime state.
- Safety rule: do not run `omx setup --scope project` as the default integration path for this repository.
- Log file path: `log/2026-04-01/omx-integration/omx-safe-integration-session.md`

# Session Timeline

1. Cloned `https://github.com/Yeachan-Heo/oh-my-codex` into the repository.
2. Reviewed the OMX repository structure and main workflow surfaces.
3. Verified that this repository already had repo-local skills under `.codex/skills/`.
4. Confirmed from OMX source and tests that `omx setup --scope project` can refresh installed skills and manage project-level `AGENTS.md`.
5. Moved the OMX source checkout out of `.omx/` and into `.vendor/oh-my-codex/` so `.omx/` stays available for OMX runtime data.
6. Added a safe wrapper at `tools/omx-safe.ps1`.
7. Initially tested a separate OMX home approach, then revised the layout to match the repository preference:
   - `.codex/` as the AI control layer
   - `.omx/` as the OMX runtime layer
8. Created `.codex/AGENTS.md` as the workspace instruction surface for Codex and OMX.
9. Updated repository documentation to describe the final local OMX layout.

# Final Layout Decision

- `.vendor/oh-my-codex/`: vendored OMX source checkout
- `.codex/`: highest AI control layer for this repository
- `.codex/AGENTS.md`: top-level AI workspace guidance
- `.codex/skills/`: repository project skills
- `.omx/`: OMX runtime state, plans, logs, notepad, HUD data, and session artifacts
- `tools/omx-safe.ps1`: local wrapper that launches OMX with `CODEX_HOME` set to `.codex/`

# Files Changed

- `.gitignore`
- `README.md`
- `README.en.md`
- `.codex/AGENTS.md`
- `docs/omx-safe-integration.md`
- `tools/omx-safe.ps1`
- `log/2026-04-01/omx-integration/omx-safe-integration-session.md`

# Verification

- Confirmed from OMX source that user-scope setup uses `CODEX_HOME` and that OMX runtime state remains under `.omx/`.
- Confirmed from OMX source that session instruction composition reads `CODEX_HOME/AGENTS.md` and project-root `AGENTS.md`, so moving the control layer into `.codex/AGENTS.md` is compatible with the wrapper approach.
- Parsed `tools/omx-safe.ps1` successfully with the PowerShell parser after the final layout update.
- Confirmed `.codex/AGENTS.md` exists and root `AGENTS.md` is absent in the final state.

# Not Yet Run

- `npm install` inside `.vendor/oh-my-codex/`
- `npm run build` inside `.vendor/oh-my-codex/`
- `tools/omx-safe.ps1 setup --scope user`
- Live launch smoke test of OMX in this repository

# Risks And Follow-Ups

- Running `omx setup --scope user` through the wrapper will intentionally allow OMX to manage prompts, agents, and config inside `.codex/`; that is aligned with the final layout, but it should still be treated as a deliberate step.
- If a future integration requires root-level project instructions for non-OMX tooling, that would need a separate decision because the current design intentionally keeps the AI control layer under `.codex/`.
- A practical next step is to build the vendored OMX checkout and run a small smoke test through `tools/omx-safe.ps1`.
