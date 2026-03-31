# Tenant Field Binding Writer

- Request summary: Create tenant field bindings for customer `ABC` from sampled Check Point firewall and McAfee ePO Splunk exports.
- Target tenant: `abc`
- Target SIEM: `splunk`

## Rule packs and mapping files used

- Device `checkpoint-fw`
  - rule pack: `rules/detections/network/firewall/base/` plus `rules/analysts/network/firewall/base/`
  - mapping file: `mappings/detections/network/firewall/firewall.fields.yaml`
- Device `mcafee-epo`
  - rule pack: `rules/detections/category/antivirus/`
  - mapping file: `mappings/detections/category/antivirus/antivirus.fields.yaml`

## Canonical to SIEM bindings written

- `tenants/abc/bindings/fields/checkpoint-fw.fields.yaml`
  - `time -> _time`
  - `src_endpoint.ip -> src_ip`
  - `src_endpoint.port -> src_port`
  - `src_endpoint.zone -> inzone`
  - `dst_endpoint.ip -> dest_ip`
  - `dst_endpoint.port -> dest_port`
  - `dst_endpoint.zone -> outzone`
  - `canonical.event.action -> action`
  - `firewall_rule.name -> rule_name`
  - `network_connection_info.protocol_name -> proto`
  - dataset `traffic`: `count -> connection_count`
- `tenants/abc/bindings/fields/mcafee-epo.fields.yaml`
  - `time -> _time`
  - `canonical.event.action -> action`
  - `malware.name -> signature`
  - `file.name -> TargetName`
  - `file.path -> TargetPath`
  - `file.hashes -> file_hash`
  - `device.hostname -> dest_host`
  - `device.ip -> dest_ip`
  - `user.name -> user`
  - `process.name -> source_process_name`

## Evidence notes

- Check Point binding chose `inzone` and `outzone` because those fields were clearly populated in the sampled export and map more reliably than leaving zone coverage on blank aliases.
- McAfee binding chose endpoint-oriented fields such as `dest_host` and `dest_ip` instead of generic log transport fields because the sampled event showed `host` and `dvc` behaving like log forwarder context rather than the protected endpoint identity.

## Validation

- Validation run: `python project-root/main.py validate-tenant --tenant-id abc`
- Result: valid with one expected warning about the missing generated deployment manifest.

## Mapping gaps

- No canonical mapping gaps were found.
- `$detection-mapping-ocsf` was not needed.
