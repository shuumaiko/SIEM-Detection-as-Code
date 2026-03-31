# Rule Merge Log Template

Use this template when recording a merge session under `log/YYYY-MM-DD/merge-rule-into-base/`.

```md
# Rule Merge Log - YYYY-MM-DD

## Summary

- Source import batch:
- Reviewer:
- Scope:

## Rule Changes

### <imported-rule-identifier>

- Classification: `detection` | `detection_base` | `analyst`
- Action: `created-new` | `merged-into-existing` | `created-base-and-analyst`
- Source file:
- Target file:
- Logic preserved: yes | no
- Notes:

### Metadata updates

- `references`:
- `author`:
- `date` or `modified`:
- `tags`:
- `fields`:
- `level`:

### Query updates

- `x_query` changed: yes | no
- Query notes:

### Deferred suggestions

- Proposed `logsource` changes:
- Proposed MITRE ATT&CK changes:
- Proposed `detection` or `correlation` changes:
```
