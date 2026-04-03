# Tenant Field Binding Writer

## Request Summary

Write minimal deployable field bindings for tenant `xyz` on `splunk` for:

- `checkpoint-fw`
- `mcafee-epo`

## Rule Packs And Mapping Files Used

- Check Point firewall pack
  - rules: `rules/detections/network/firewall/base/*`
  - mapping: `mappings/detections/network/firewall/firewall.fields.yaml`
- McAfee antivirus pack
  - rules: `rules/detections/category/antivirus/*`
  - mapping: `mappings/detections/category/antivirus/antivirus.fields.yaml`

## Canonical To SIEM Bindings Written

- `checkpoint-fw.fields.yaml`
  - `time -> _time`
  - `src_endpoint.ip -> src_ip`
  - `src_endpoint.port -> s_port`
  - `src_endpoint.zone -> src_zone`
  - `dst_endpoint.ip -> dest_ip`
  - `dst_endpoint.port -> service`
  - `dst_endpoint.zone -> dest_zone`
  - `canonical.event.action -> action`
  - `firewall_rule.name -> rule_name`
  - `network_connection_info.protocol_name -> proto`
  - dataset override: `traffic.count -> connection_count`
- `mcafee-epo.fields.yaml`
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

## Validation

- Automated tenant validation: planned after file creation

## Unresolved Gaps

- No mapping-layer gaps found from the sampled logs
- Check Point count semantics were approximated with `connection_count` because sampled events did not expose a direct `event_count` field
