# Tenant Onboard From SIEM Log

## Request Summary

Onboard new tenant `xyz` for `splunk` from two sampled SIEM exports:

- `checkpoint-log.csv`
- `mcafee-log.csv`

## Sampled Log Evidence Used

- `checkpoint-log.csv`: sampled header plus first events only, not the full file
  - product hint: `Firewall`
  - hostname: `CP-SMC`
  - eventtype: `Network_Traffic`
  - index: `checkpoint`
  - sourcetype: `cp_log`
  - key fields observed: `src_ip`, `s_port`, `src_zone`, `dest_ip`, `service`, `dest_zone`, `action`, `rule_name`, `proto`, `connection_count`
- `mcafee-log.csv`: sampled header plus first events only, not the full file
  - analyzer: `Trellix Endpoint Security`
  - vendor product: `mcafee_epo`
  - eventtype: `mcafee_epo_hip_file`
  - index: `epav`
  - sourcetype: `mcafee:epo:syslog`
  - key fields observed: `signature`, `TargetName`, `TargetPath`, `file_hash`, `dest_host`, `dest_ip`, `user`, `source_process_name`, `action`

## Tenant Config Files Changed

- `tenants/xyz/tenant.yaml`
- `tenants/xyz/devices/device_checkpoint_fw.yaml`
- `tenants/xyz/devices/device_mcafee_epo.yaml`
- `tenants/xyz/logsources/logsource_checkpoint_fw.yaml`
- `tenants/xyz/logsources/logsource_mcafee_epo.yaml`
- `tenants/xyz/bindings/ingest/binding_checkpoint_fw.yaml`
- `tenants/xyz/bindings/ingest/binding_mcafee_epo.yaml`

## Field Binding Files Changed

- `tenants/xyz/bindings/fields/checkpoint-fw.fields.yaml`
- `tenants/xyz/bindings/fields/mcafee-epo.fields.yaml`

## Mapping Repair

Not needed. Existing mapping files were sufficient:

- `mappings/detections/network/firewall/firewall.fields.yaml`
- `mappings/detections/category/antivirus/antivirus.fields.yaml`

## Validation

- Automated tenant validation: planned after file creation
- Deployment manifest generation: intentionally not created by hand in this workflow

## Assumptions

- `tenant_id` is `xyz`
- tenant timezone is assumed as `Asia/Ho_Chi_Minh`
- deployment scope is intended to support the existing firewall traffic and antivirus rule packs already present in the repository

