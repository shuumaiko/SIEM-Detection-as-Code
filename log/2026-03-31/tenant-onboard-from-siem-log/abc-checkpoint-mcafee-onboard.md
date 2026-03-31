# Tenant Onboard From SIEM Log

- Request summary: Onboard customer `ABC` from Splunk-exported `checkpoint-log.csv` and `mcafee-log.csv` using `$tenant-onboard-from-siem-log`.
- Sampled log evidence used:
  - `checkpoint-log.csv`: CSV header plus representative traffic events showing `product=Firewall`, `eventtype=Network_Traffic`, `index=checkpoint`, `sourcetype=cp_log`, hostname `CP-SMC`, and network fields such as `src_ip`, `dest_ip`, `src_port`, `dest_port`, `inzone`, `outzone`, `rule_name`, and `proto`.
  - `mcafee-log.csv`: CSV header plus representative antivirus events showing analyzer `Trellix Endpoint Security`, observed product `ENDP_AM_1070LYNX`, `eventtype=mcafee_epo_hip_file`, `index=epav`, `sourcetype=mcafee:epo:syslog`, and endpoint fields such as `signature`, `TargetName`, `TargetPath`, `file_hash`, `dest_host`, `dest_ip`, `user`, and `source_process_name`.

## Tenant files created

- `tenants/abc/tenant.yaml`
- `tenants/abc/devices/device_checkpoint_fw.yaml`
- `tenants/abc/devices/device_mcafee_epo.yaml`
- `tenants/abc/logsources/logsource_checkpoint_fw.yaml`
- `tenants/abc/logsources/logsource_mcafee_epo.yaml`
- `tenants/abc/bindings/ingest/binding_checkpoint_fw.yaml`
- `tenants/abc/bindings/ingest/binding_mcafee_epo.yaml`
- `tenants/abc/bindings/fields/checkpoint-fw.fields.yaml`
- `tenants/abc/bindings/fields/mcafee-epo.fields.yaml`

## Inferred structure

- `tenant_id`: `abc`
- `siem_id`: `splunk`
- device `checkpoint-fw`
  - dataset `traffic`
  - observed ingest `index=checkpoint`, `sourcetype=cp_log`
  - catalog reference used: `NSM:Flow`
- device `mcafee-epo`
  - dataset `mcafee-epo-syslog`
  - observed ingest `index=epav`, `sourcetype=mcafee:epo:syslog`
  - catalog reference used: `custom`

## Field binding outcome

- `bindings/fields` created for both `checkpoint-fw` and `mcafee-epo`.
- `$detection-mapping-ocsf` was not needed.
- Existing mapping files reused:
  - `mappings/detections/network/firewall/firewall.fields.yaml`
  - `mappings/detections/category/antivirus/antivirus.fields.yaml`

## Validation

- Command run: `python project-root/main.py validate-tenant --tenant-id abc`
- Result: valid
- Summary: `files_checked=9`, `errors=0`, `warnings=1`
- Warning: no generated deployment manifest exists yet under `tenants/abc/deployments/rule-deployments.yaml`, which is expected because this workflow does not hand-write deployment manifests.

## Assumptions

- `tenant_id` was normalized from the customer label `ABC` to lowercase `abc` to match the tenant schema.
- `timezone` was set to `Asia/Bangkok` from the observed `+07:00` timestamps in the sampled exports.
- Deployment enablement was intentionally left for the repository generation flow rather than hand-writing `rule-deployments.yaml`.
