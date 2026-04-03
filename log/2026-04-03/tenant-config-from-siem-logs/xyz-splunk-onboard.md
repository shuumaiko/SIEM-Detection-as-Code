# Tenant Config From SIEM Logs

## Request Summary

Create tenant-layer configuration for tenant `xyz` on `splunk` from sampled
Check Point and McAfee ePO logs.

## Files Changed

- `tenants/xyz/tenant.yaml`
- `tenants/xyz/devices/device_checkpoint_fw.yaml`
- `tenants/xyz/devices/device_mcafee_epo.yaml`
- `tenants/xyz/logsources/logsource_checkpoint_fw.yaml`
- `tenants/xyz/logsources/logsource_mcafee_epo.yaml`
- `tenants/xyz/bindings/ingest/binding_checkpoint_fw.yaml`
- `tenants/xyz/bindings/ingest/binding_mcafee_epo.yaml`

## Inferred Device And Dataset Structure

- `checkpoint-fw`
  - device_type: `firewall`
  - dataset_id: `traffic`
  - catalog_logsource: `NSM:Flow`
  - suggested category/service used for rule alignment: `firewall` / `traffic`
- `mcafee-epo`
  - device_type: `endpoint`
  - dataset_id: `mcafee-epo-syslog`
  - no stronger catalog entry matched than the rule-driven antivirus pack, so dataset naming followed the existing repo pattern

## Observed Ingest Evidence

- Check Point:
  - index: `checkpoint`
  - sourcetype: `cp_log`
- McAfee ePO:
  - index: `epav`
  - sourcetype: `mcafee:epo:syslog`

## Rule-Driven Naming Inputs

- Firewall dataset aligned to `rules/detections/network/firewall/*` with `service: traffic`
- McAfee dataset aligned to `rules/detections/category/antivirus/*` and existing repo usage of `mcafee-epo-syslog`

## Delegation Notes

- Field binding handled through the tenant-field-binding-writer workflow
- Detection mapping repair was not needed

## Validation

- Automated tenant validation: planned after file creation

## Assumptions

- tenant timezone assumed from operator context
- deployment manifest remains generated output, not hand-authored source

