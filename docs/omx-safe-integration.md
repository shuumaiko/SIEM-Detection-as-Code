# Safe OMX Integration

This repository keeps AI control surfaces under `.codex/` and OMX runtime data under `.omx/`.
That means OMX should be integrated here in a way that respects that split.

## Why Not Use Project Scope Directly

Do not run `omx setup --scope project` directly in this repository unless you explicitly want OMX to manage `.codex/`.

Reasons:

- this repo already has project-local skills in `.codex/skills/`
- we want `.codex/` to remain the highest AI control layer
- we want `.omx/` to stay reserved for OMX runtime data
- `omx setup --scope project` would create or manage a root `AGENTS.md`, which is not the layout we want here

## Safe Layout In This Repo

- `.vendor/oh-my-codex/`: local OMX source checkout
- `.codex/`: AI control layer for this repository
- `.codex/AGENTS.md`: top-level workspace instructions for Codex and OMX
- `.codex/skills/`: repo-local project skills
- `.codex/prompts/`, `.codex/agents/`, `.codex/config.toml`: OMX-managed Codex surfaces when installed through the wrapper
- `.omx/`: OMX runtime state, plans, logs, notepad, and HUD data

This keeps the AI control layer in `.codex/` while leaving OMX state in `.omx/`.

## One-Time Build

Build the local OMX checkout before using the wrapper:

```powershell
cd .vendor\oh-my-codex
npm install
npm run build
```

## Safe Wrapper

Use the wrapper at `tools/omx-safe.ps1`.
It sets `CODEX_HOME` to `.codex/` and forwards all arguments to the local OMX CLI.

Examples:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\omx-safe.ps1 setup --scope user
powershell -ExecutionPolicy Bypass -File .\tools\omx-safe.ps1 doctor
powershell -ExecutionPolicy Bypass -File .\tools\omx-safe.ps1 --high
powershell -ExecutionPolicy Bypass -File .\tools\omx-safe.ps1 team 2:executor "review current branch"
```

## Recommended Usage Rules

- keep using `.codex/` as the repository's authoritative AI control layer
- keep using `.codex/skills/` as the repository's project skill set
- use OMX as the runtime and workflow layer on top of that control surface
- keep `.codex/AGENTS.md` updated instead of using a root `AGENTS.md`
- prefer `setup --scope user` through the wrapper
- avoid `setup --scope project` unless you intentionally want a root `AGENTS.md`

## Practical Workflow

1. Build OMX in `.vendor/oh-my-codex/`.
2. Run `tools/omx-safe.ps1 setup --scope user`.
3. Launch OMX through `tools/omx-safe.ps1`.
4. Keep project-specific domain skills and instructions in `.codex/`.
5. Let OMX use `.omx/` only for runtime state and workflow artifacts.

## Notes

- The wrapper intentionally points `CODEX_HOME` at the repository's `.codex/`.
- OMX runtime files created under `.omx/` are ignored by git.
- If you run `omx setup --scope user` through the wrapper, OMX-managed prompts, agents, and config will be written into `.codex/` by design.
