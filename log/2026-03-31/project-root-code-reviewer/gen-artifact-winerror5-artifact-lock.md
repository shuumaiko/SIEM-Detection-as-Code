# Project-Root Review: Gen-Artifact WinError 5 On Artifact File

## Request Summary

Review why `gen-artifact` intermittently fails on Windows with:

`PermissionError: [WinError 5] Access is denied: 'D:\Personal\SIEM-Detection-as-Code\artifacts\demo\splunk\analysts\network\firewall\base\net_fw_possible_scan_ftp_port_21_external_allowed.yaml'`

## Review Scope

- Goal: determine whether this is a code-path bug or an external file-lock issue
- Suspected risk: `gen-artifact` rewrites artifact files in a way that is fragile on Windows when another process temporarily holds a handle
- Entry workflow: `python project-root/main.py gen-artifact --tenant-id demo`
- Main files inspected:
  - `project-root/app/usecases/export_rules.py`
  - `project-root/infrastructure/repositories/file_rule_repository.py`
  - `project-root/main.py`
- Log path: `log/2026-03-31/project-root-code-reviewer/gen-artifact-winerror5-artifact-lock.md`

## Commands Run

- inspected artifact write and rewrite code paths in `project-root/`
- checked file attributes for `artifacts/demo/splunk/analysts/network/firewall/base/net_fw_possible_scan_ftp_port_21_external_allowed.yaml`

## Findings

1. The file is not persistently read-only.
   - Observed attributes: `Archive`
   - Observed `IsReadOnly`: `False`
   - This makes a static permission or read-only flag much less likely.

2. `gen-artifact` performs multiple destructive or overwrite operations against the same artifact tree in one run.
   - `project-root/infrastructure/repositories/file_rule_repository.py:149-165`
     - removes the full tenant artifact tree with `shutil.rmtree(target_root)`
     - recreates directories
     - writes each artifact file
   - `project-root/app/usecases/export_rules.py:47-50`
     - after saving artifacts and deployment manifest, reloads the tenant and immediately calls `sync_artifact_enabled_states(...)`
   - `project-root/infrastructure/repositories/file_rule_repository.py:196-226`
     - reopens each artifact file and rewrites it in place a second time to sync `targets.enabled`

3. The intermittent Windows-specific behavior is most consistent with a temporary external file lock, not a deterministic repository rule bug.
   - On Windows, `PermissionError: [WinError 5] Access is denied` commonly occurs when another process holds the file or directory without compatible sharing flags.
   - In this flow, the vulnerable points are:
     - deleting the old artifact tree
     - opening a freshly created artifact for the first write
     - reopening that same artifact for the second write in `sync_artifact_enabled_states`
   - Because the failure is intermittent, the most likely external lockers are editor extensions, preview/indexing services, antivirus scanning, or overlapping `gen-artifact` runs.

## Open Questions Or Assumptions

- No full traceback was provided, so this review cannot prove whether the failure came from `rmtree(...)`, the first `open(..., "w")`, or the second `open(..., "w")`.
- The diagnosis assumes the same command usually succeeds against the same path, which points away from ACL misconfiguration.

## Verification Summary

- Confirmed the target artifact file is not read-only.
- Confirmed the current `gen-artifact` path deletes and rewrites artifacts, then rewrites them again in the same command.
- This review did not modify source files.
