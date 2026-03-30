# Rule Merge Log - 2026-03-30

## Summary

- Source import batch: `rule_pre_deployment.json`
- Reviewer: Codex
- Scope: Merge imported rules No 1 through No 10 into canonical `rules/` content for Splunk SIEM monitoring and firewall scan detections.

## Rule Changes

### No 1 - No Log from Host over 24 hours

- Classification: `analyst`
- Action: `created-new`
- Source file: `rule_pre_deployment.json`
- Target files:
  - `rules/detections/application/splunk/base/siem_log_activity.yml`
  - `rules/analysts/application/splunk/base/siem_no_log_from_host_over_24h.yaml`
- Logic preserved: yes
- Notes: Created one shared Splunk activity base rule and modeled the imported last-seen gap query as an analyst-facing inactivity rule keyed by `host`.

### Metadata updates

- `references`: added `source_ref`
- `author`: set to repository maintainer
- `date` or `modified`: set to `2026-03-30`
- `tags`: normalized to monitoring-oriented tags
- `fields`: limited to host-oriented last-seen fields used by the imported SPL
- `level`: set to `medium` from imported `Alert_Severity`

### Query updates

- `x_query` changed: yes
- Query notes: Preserved the imported `tstats` pipeline as-is in `x_query.splunk`.

### Deferred suggestions

- Proposed `logsource` changes: none
- Proposed MITRE ATT&CK changes: none
- Proposed `detection` or `correlation` changes: none

### No 2 - No Log from Source over 1 hour

- Classification: `analyst`
- Action: `created-new`
- Source file: `rule_pre_deployment.json`
- Target file: `rules/analysts/application/splunk/base/siem_no_log_from_source_over_1h.yaml`
- Logic preserved: yes
- Notes: Reused the shared `siem_log_activity` base rule and modeled the imported last-seen gap query as an analyst rule keyed by `source`.

### Metadata updates

- `references`: added `source_ref`
- `author`: set to repository maintainer
- `date` or `modified`: set to `2026-03-30`
- `tags`: normalized to monitoring-oriented tags
- `fields`: limited to source-oriented last-seen fields used by the imported SPL
- `level`: set to `high` from imported `Alert_Severity`

### Query updates

- `x_query` changed: yes
- Query notes: Preserved the imported `tstats` pipeline and retained the `sources_filter` macro reference in `x_query.splunk`.

### Deferred suggestions

- Proposed `logsource` changes: none
- Proposed MITRE ATT&CK changes: none
- Proposed `detection` or `correlation` changes: none

### No 3 - Request reached over threshold

- Classification: `analyst`
- Action: `merged-into-existing`
- Source file: `rule_pre_deployment.json`
- Target file: `rules/analysts/network/firewall/base/net_fw_request_reached_over_threshold.yaml`
- Logic preserved: yes
- Notes: Updated the existing canonical analyst rule to carry the imported threshold-oriented firewall summary SPL while keeping the existing external-connection semantic anchor.

### Metadata updates

- `references`: added `source_ref`
- `author`: unchanged
- `date` or `modified`: updated `modified` to `2026-03-30`
- `tags`: unchanged
- `fields`: expanded to cover the imported summary output
- `level`: unchanged

### Query updates

- `x_query` changed: yes
- Query notes: Replaced hardcoded `index=firewall sourcetype=pan:traffic` with `index=$index$ sourcetype=$sourcetype$` while preserving the imported aggregation logic and threshold.

### Deferred suggestions

- Proposed `logsource` changes: none
- Proposed MITRE ATT&CK changes: none
- Proposed `detection` or `correlation` changes: none

### No 4 - Posible SCAN FTP Port (21) (External Allowed)

- Classification: `analyst`
- Action: `created-new`
- Source file: `rule_pre_deployment.json`
- Target files:
  - `rules/detections/network/firewall/base/fw_connection_port_21.yml`
  - `rules/analysts/network/firewall/base/net_fw_possible_scan_ftp_port_21_external_allowed.yaml`
- Logic preserved: yes
- Notes: Introduced a reusable FTP port-21 base rule and kept the imported analyst SPL as an analyst-facing summary of non-blocked external traffic.

### Metadata updates

- `references`: added `source_ref`
- `author`: set to repository maintainer
- `date` or `modified`: set to `2026-03-30`
- `tags`: normalized to scan/discovery tags
- `fields`: aligned to the imported summary output fields
- `level`: set to `high` from imported `Alert_Severity`

### Query updates

- `x_query` changed: yes
- Query notes: Replaced environment-specific source scoping with `index=$index$ sourcetype=$sourcetype$` and preserved the imported external/non-blocked logic.

### Deferred suggestions

- Proposed `logsource` changes: none
- Proposed MITRE ATT&CK changes: kept `attack.t1046` for this scan family instead of the inconsistent imported technique IDs used elsewhere in the spreadsheet
- Proposed `detection` or `correlation` changes: consider introducing a first-class semantic concept for public-exposed service monitoring if more analyst summaries of this kind are imported

### No 5 - Posible SCAN FTP Port (21) Per Host (Excessive Blocked)

- Classification: `analyst`
- Action: `created-new`
- Source file: `rule_pre_deployment.json`
- Target file: `rules/analysts/network/firewall/base/net_fw_possible_scan_ftp_port_21_blocked_per_host.yaml`
- Logic preserved: yes
- Notes: Reused the shared port-21 base rule and modeled the imported blocked-count threshold as an analyst rule grouped by `src_ip` and `dest_ip`.

### Metadata updates

- `references`: added `source_ref`
- `author`: set to repository maintainer
- `date` or `modified`: set to `2026-03-30`
- `tags`: normalized to scan/discovery tags
- `fields`: aligned to the imported blocked summary output
- `level`: set to `medium` from imported `Alert_Severity`

### Query updates

- `x_query` changed: yes
- Query notes: Replaced environment-specific source scoping with `index=$index$ sourcetype=$sourcetype$` and preserved the imported blocked threshold.

### Deferred suggestions

- Proposed `logsource` changes: none
- Proposed MITRE ATT&CK changes: kept `attack.t1046` for this scan family instead of the inconsistent imported technique IDs used elsewhere in the spreadsheet
- Proposed `detection` or `correlation` changes: none

### No 6 - Posible SCAN FTP Port (21) To Multiple Host

- Classification: `analyst`
- Action: `created-new`
- Source file: `rule_pre_deployment.json`
- Target file: `rules/analysts/network/firewall/base/net_fw_possible_scan_ftp_port_21_to_multiple_hosts.yaml`
- Logic preserved: yes
- Notes: Reused the shared port-21 base rule and modeled the imported multi-destination threshold as an analyst rule keyed by `src_ip`.

### Metadata updates

- `references`: added `source_ref`
- `author`: set to repository maintainer
- `date` or `modified`: set to `2026-03-30`
- `tags`: normalized to scan/discovery tags
- `fields`: aligned to the imported summary output
- `level`: set to `medium` from imported `Alert_Severity`

### Query updates

- `x_query` changed: yes
- Query notes: Replaced environment-specific source scoping with `index=$index$ sourcetype=$sourcetype$` and preserved the imported distinct-host threshold.

### Deferred suggestions

- Proposed `logsource` changes: none
- Proposed MITRE ATT&CK changes: kept `attack.t1046` for this scan family instead of the inconsistent imported technique IDs used elsewhere in the spreadsheet
- Proposed `detection` or `correlation` changes: none

### No 7 - Posible SCAN RDP Port (3389) (External Allowed)

- Classification: `analyst`
- Action: `created-new`
- Source file: `rule_pre_deployment.json`
- Target files:
  - `rules/detections/network/firewall/base/fw_connection_port_3389.yml`
  - `rules/analysts/network/firewall/base/net_fw_possible_scan_rdp_port_3389_external_allowed.yaml`
- Logic preserved: yes
- Notes: Introduced a reusable RDP port-3389 base rule and kept the imported analyst SPL as an analyst-facing summary of non-blocked external traffic.

### Metadata updates

- `references`: added `source_ref`
- `author`: set to repository maintainer
- `date` or `modified`: set to `2026-03-30`
- `tags`: normalized to scan/discovery tags
- `fields`: aligned to the imported summary output fields
- `level`: set to `high` from imported `Alert_Severity`

### Query updates

- `x_query` changed: yes
- Query notes: Replaced environment-specific source scoping with `index=$index$ sourcetype=$sourcetype$` and preserved the imported external/non-blocked logic.

### Deferred suggestions

- Proposed `logsource` changes: none
- Proposed MITRE ATT&CK changes: kept `attack.t1046` for this scan family instead of the inconsistent imported technique IDs used elsewhere in the spreadsheet
- Proposed `detection` or `correlation` changes: consider introducing a first-class semantic concept for public-exposed service monitoring if more analyst summaries of this kind are imported

### No 8 - Posible SCAN RDP Port (3389) Per Host (Excessive Blocked)

- Classification: `analyst`
- Action: `created-new`
- Source file: `rule_pre_deployment.json`
- Target file: `rules/analysts/network/firewall/base/net_fw_possible_scan_rdp_port_3389_blocked_per_host.yaml`
- Logic preserved: yes
- Notes: Reused the shared port-3389 base rule and modeled the imported blocked-count threshold as an analyst rule grouped by `src_ip` and `dest_ip`.

### Metadata updates

- `references`: added `source_ref`
- `author`: set to repository maintainer
- `date` or `modified`: set to `2026-03-30`
- `tags`: normalized to scan/discovery tags
- `fields`: aligned to the imported blocked summary output
- `level`: set to `medium` from imported `Alert_Severity`

### Query updates

- `x_query` changed: yes
- Query notes: Replaced environment-specific source scoping with `index=$index$ sourcetype=$sourcetype$` and preserved the imported blocked threshold.

### Deferred suggestions

- Proposed `logsource` changes: none
- Proposed MITRE ATT&CK changes: kept `attack.t1046` for this scan family instead of the inconsistent imported technique IDs used elsewhere in the spreadsheet
- Proposed `detection` or `correlation` changes: none

### No 9 - Posible SCAN RDP Port (3389)To Multiple Host

- Classification: `analyst`
- Action: `created-new`
- Source file: `rule_pre_deployment.json`
- Target file: `rules/analysts/network/firewall/base/net_fw_possible_scan_rdp_port_3389_to_multiple_hosts.yaml`
- Logic preserved: yes
- Notes: Reused the shared port-3389 base rule and modeled the imported multi-destination threshold as an analyst rule keyed by `src_ip`.

### Metadata updates

- `references`: added `source_ref`
- `author`: set to repository maintainer
- `date` or `modified`: set to `2026-03-30`
- `tags`: normalized to scan/discovery tags
- `fields`: aligned to the imported summary output
- `level`: set to `medium` from imported `Alert_Severity`

### Query updates

- `x_query` changed: yes
- Query notes: Replaced environment-specific source scoping with `index=$index$ sourcetype=$sourcetype$` and preserved the imported distinct-host threshold.

### Deferred suggestions

- Proposed `logsource` changes: none
- Proposed MITRE ATT&CK changes: kept `attack.t1046` for this scan family instead of the inconsistent imported technique IDs used elsewhere in the spreadsheet
- Proposed `detection` or `correlation` changes: none

### No 10 - Posible SCAN SSH Port (22) (External Allowed)

- Classification: `analyst`
- Action: `created-new`
- Source file: `rule_pre_deployment.json`
- Target files:
  - `rules/detections/network/firewall/base/fw_connection_port_22.yml`
  - `rules/analysts/network/firewall/base/net_fw_possible_scan_ssh_port_22_external_allowed.yaml`
- Logic preserved: yes
- Notes: Introduced a reusable SSH port-22 base rule and kept the imported analyst SPL as an analyst-facing summary of non-blocked external traffic.

### Metadata updates

- `references`: added `source_ref`
- `author`: set to repository maintainer
- `date` or `modified`: set to `2026-03-30`
- `tags`: normalized to scan/discovery tags
- `fields`: aligned to the imported summary output fields
- `level`: set to `high` from imported `Alert_Severity`

### Query updates

- `x_query` changed: yes
- Query notes: Replaced environment-specific source scoping with `index=$index$ sourcetype=$sourcetype$` and preserved the imported external/non-blocked logic.

### Deferred suggestions

- Proposed `logsource` changes: none
- Proposed MITRE ATT&CK changes: kept `attack.t1046` for this scan family instead of the inconsistent imported technique IDs used elsewhere in the spreadsheet
- Proposed `detection` or `correlation` changes: consider introducing a first-class semantic concept for public-exposed service monitoring if more analyst summaries of this kind are imported

## Modeling Notes

- Imported No 1 and No 2 were modeled as analyst rules over a shared Splunk SIEM activity base rule because their main value is the last-seen gap calculation, not a standalone semantic detection.
- Imported No 4 through No 10 were split into reusable port-specific base rules and analyst-facing summary rules to keep the repo's semantic layer reusable while still preserving the imported SPL.
- Imported firewall scan rows No 5 through No 10 carried inconsistent ATT&CK technique IDs in the spreadsheet. The canonical rules keep the broader and more coherent `attack.discovery` plus `attack.t1046` scan-family tagging for now.
