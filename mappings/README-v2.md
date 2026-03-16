# Mapping Skeleton V2

This file documents the proposed mapping folder structure for the current
content-team-focused architecture.

```text
mappings/
  detections/
    <domain>/
      <product>/
        <product>.fields.yml

tenants/
  <tenant>/
    bindings/
      fields/
        <device>.fields.yml
```

Meaning:

- `mappings/detections/`: source rule field -> canonical field
- `tenants/.../bindings/fields/`: canonical field -> tenant SIEM field

These files are skeleton examples for v1.0 architecture and do not replace the
existing legacy mapping folders yet.
