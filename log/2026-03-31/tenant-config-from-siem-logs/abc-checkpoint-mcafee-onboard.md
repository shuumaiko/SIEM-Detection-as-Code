# Tenant Config From SIEM Logs

- Request summary: Create tenant-layer source files for customer `ABC` from `checkpoint-log.csv` and `mcafee-log.csv`.
- Tenant files changed:
  - `tenants/abc/tenant.yaml`
  - `tenants/abc/devices/device_checkpoint_fw.yaml`
  - `tenants/abc/devices/device_mcafee_epo.yaml`
  - `tenants/abc/logsources/logsource_checkpoint_fw.yaml`
  - `tenants/abc/logsources/logsource_mcafee_epo.yaml`
  - `tenants/abc/bindings/ingest/binding_checkpoint_fw.yaml`
  - `tenants/abc/bindings/ingest/binding_mcafee_epo.yaml`

## Inferred device and dataset structure

- `checkpoint-fw`
  - device type: `firewall`
  - dataset: `traffic`
  - rule-driven logsource fit: `category=firewall`, `service=traffic`
- `mcafee-epo`
  - device type: `endpoint`
  - dataset: `mcafee-epo-syslog`
  - rule-driven logsource fit: `category=antivirus`, `service=any`

## Ingest evidence used

- From `checkpoint-log.csv`
  - `index: checkpoint`
  - `sourcetype: cp_log`
  - observed hostname `CP-SMC`
  - observed eventtype `Network_Traffic`
- From `mcafee-log.csv`
  - `index: epav`
  - `sourcetype: mcafee:epo:syslog`
  - observed analyzer `Trellix Endpoint Security`
  - observed eventtype `mcafee_epo_hip_file`

## Detection Catalog reference

- Check Point stream classified to `NSM:Flow` from the skill seed and kept dataset `traffic`.
- McAfee or Trellix antivirus syslog had no direct seed entry, so it was treated as `custom` and aligned to the existing antivirus rule inventory with dataset `mcafee-epo-syslog`.

## Rule inventory used for dataset decisions

- Firewall traffic rules under `rules/detections/network/firewall/base/` and analyst correlations under `rules/analysts/network/firewall/base/` drove the `traffic` dataset decision.
- Antivirus detections under `rules/detections/category/antivirus/` drove the `mcafee-epo-syslog` dataset decision.

## Delegation and validation

- `$tenant-field-binding-writer` was used conceptually and implemented in the corresponding field binding files.
- `$detection-mapping-ocsf` was not needed because existing mapping files were sufficient.
- Validation run: `python project-root/main.py validate-tenant --tenant-id abc`
- Result: valid with one expected warning about the absent generated deployment manifest.

## Assumptions

- Customer label `ABC` was stored as tenant folder and `tenant_id` value `abc` due schema constraints.
- `environment` was set to `production` because the logs came from an active Splunk deployment.
