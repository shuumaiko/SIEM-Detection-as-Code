# Rule Merge Log - 2026-03-28

## Summary

- Source import batch: `lab-enabled-rules.csv` antivirus detections
- Reviewer: Codex
- Scope: Merge 5 antivirus rules into canonical detection files and create the shared antivirus detection field mapping.

## Rule Changes

### FPT - Antivirus Hacktool Detected by AV

- Classification: `detection`
- Action: `merged-into-existing`
- Source file: `lab-enabled-rules.csv`
- Target file: `rules/detections/category/antivirus/av_hacktool.yml`
- Logic preserved: yes
- Notes: Merged the generic antivirus SPL into the existing canonical hacktool rule and corrected the previously broken `x_query` syntax while keeping the Sigma detection logic unchanged.

### Metadata updates

- `references`: unchanged
- `author`: unchanged
- `date` or `modified`: updated `modified` to `2026-03-28`
- `tags`: unchanged
- `fields`: refreshed to match the merged query output
- `level`: unchanged

### Query updates

- `x_query` changed: yes
- Query notes: Replaced the malformed query block with the lab query pattern and kept the query free of environment-specific source scoping.

### Deferred suggestions

- Proposed `logsource` changes: none
- Proposed MITRE ATT&CK changes: none
- Proposed `detection` or `correlation` changes: none

### FPT - Antivirus Ransomware Detected by AV

- Classification: `detection`
- Action: `merged-into-existing`
- Source file: `lab-enabled-rules.csv`
- Target file: `rules/detections/category/antivirus/av_ransomware.yml`
- Logic preserved: yes
- Notes: Kept the existing ransomware detection logic and normalized the query output field names to align with the new shared mapping.

### Metadata updates

- `references`: unchanged
- `author`: unchanged
- `date` or `modified`: updated `modified` to `2026-03-28`
- `tags`: unchanged
- `fields`: added `signature` to the output field list
- `level`: unchanged

### Query updates

- `x_query` changed: yes
- Query notes: Preserved the generic antivirus search logic and normalized output aliases for mapping reuse.

### Deferred suggestions

- Proposed `logsource` changes: none
- Proposed MITRE ATT&CK changes: none
- Proposed `detection` or `correlation` changes: none

### FPT - ESET - Antivirus Password Dumper Detection

- Classification: `detection`
- Action: `merged-into-existing`
- Source file: `lab-enabled-rules.csv`
- Target file: `rules/detections/category/antivirus/av_password_dumper.yml`
- Logic preserved: yes
- Notes: Added the lab ESET search pattern as the execution query while leaving the canonical Sigma-style detection block intact.

### Metadata updates

- `references`: added Sigma `source_ref`
- `author`: unchanged
- `date` or `modified`: updated `modified` to `2026-03-28`
- `tags`: unchanged
- `fields`: added the source fields needed for query output and mapping
- `level`: unchanged

### Query updates

- `x_query` changed: yes
- Query notes: Removed environment-specific `index` and `sourcetype` scoping from the imported lab query and retained the password-dumper matching semantics.

### Deferred suggestions

- Proposed `logsource` changes: none
- Proposed MITRE ATT&CK changes: none
- Proposed `detection` or `correlation` changes: none

### FPT - ESET - Antivirus Exploitation Framework Detection

- Classification: `detection`
- Action: `merged-into-existing`
- Source file: `lab-enabled-rules.csv`
- Target file: `rules/detections/category/antivirus/av_exploiting.yml`
- Logic preserved: yes
- Notes: Added the lab exploitation-framework SPL as `x_query` and normalized the rule metadata to the repo detection schema style.

### Metadata updates

- `references`: added Sigma `source_ref`
- `author`: unchanged
- `date` or `modified`: updated `modified` to `2026-03-28`
- `tags`: unchanged
- `fields`: added the source fields needed for query output and mapping
- `level`: unchanged

### Query updates

- `x_query` changed: yes
- Query notes: Removed environment-specific source scoping while preserving the imported exploitation-framework terms and aggregation shape.

### Deferred suggestions

- Proposed `logsource` changes: none
- Proposed MITRE ATT&CK changes: none
- Proposed `detection` or `correlation` changes: none

### FPT - ESET - Antivirus Web Shell Detection

- Classification: `detection`
- Action: `merged-into-existing`
- Source file: `lab-enabled-rules.csv`
- Target file: `rules/detections/category/antivirus/av_webshell.yml`
- Logic preserved: yes
- Notes: Added the generic ESET web-shell SPL to the canonical rule and kept the existing Sigma web-shell matching logic unchanged.

### Metadata updates

- `references`: added Sigma `source_ref`
- `author`: unchanged
- `date` or `modified`: updated `modified` to `2026-03-28`
- `tags`: unchanged
- `fields`: added the source fields needed for query output and mapping
- `level`: unchanged

### Query updates

- `x_query` changed: yes
- Query notes: Removed environment-specific source scoping from the imported query and normalized output aliases for the shared antivirus mapping.

### Deferred suggestions

- Proposed `logsource` changes: none
- Proposed MITRE ATT&CK changes: none
- Proposed `detection` or `correlation` changes: none

## Mapping Changes

- Created `mappings/detections/category/antivirus/antivirus.fields.yaml` as the shared antivirus detection field dictionary.
- Mapped the detection and output fields used by the 5 merged rules to `canonical.*` fields informed by OCSF Detection Finding, Malware, File, Device, User, and Process semantics.
