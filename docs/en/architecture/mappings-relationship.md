# Mapping Component Architecture

> Vietnamese source: [mappings-relationship.md](../../architecture/mappings-relationship.md)

## 1. Purpose and Scope

This document defines the role, responsibility boundaries, and organizational principles of the `mappings/` directory in the `SIEM-Detection-as-Code` repository.

The document focuses on the mapping layer used for detection content and tenant-specific rendering. It does not attempt to describe the entire path from raw logs to parser implementation for each SIEM.

## 2. Role of the Mapping Layer

In the current architecture, `mappings/` is the contract layer used to normalize fields and detection semantics.

Its primary objectives are:

- provide a shared field vocabulary for writing and maintaining detection rules
- reduce rule dependence on source-specific naming conventions
- connect `source rule field` to the project's `canonical field`
- provide the basis for connecting `canonical field` to the tenant's actual SIEM field
- support tenant-based rendering while a generic converter is still incomplete

Under this model:

- `rules/` defines the behavior to be detected
- `mappings/` defines how fields are understood in a normalized form
- `tenants/` defines which fields a tenant actually has and where they are deployed

## 3. Standard Folder Model

At the current stage, the mapping layer is organized around 2 main branches:

```text
mappings/
  detections/
    <domain>/
      <product>/
        *.fields.yml
tenants/
  <tenant>/
    bindings/
      ingest/
        *.yaml
      fields/
        *.fields.yml
```

Organizational principles:

- `mappings/detections/` stores normalized mappings from `source rule field` to `canonical field`
- `tenants/.../bindings/fields/` stores mappings from `canonical field` to `tenant SIEM field`
- the taxonomy of `mappings/detections/` must stay aligned with the taxonomy of `rules/`
- rule-by-rule mapping duplication should be avoided when multiple rules share the same field vocabulary

## 4. `mappings/detections/`

`mappings/detections/` is the standard mapping layer on the detection-content side.

Role:

- normalize source rule fields into canonical fields
- support rule ingestion from multiple field vocabularies
- provide a shared field dictionary by domain or product

Example:

```text
rules/
  detections/
    network/
      firewall/
        base/
          net_fw_rpc-to-the-internet.yml

mappings/
  detections/
    network/
      firewall/
        firewall.fields.yml
```

In this model, `firewall.fields.yml` is the shared field dictionary for a firewall rule family; it is not the private mapping file of a single rule.

## 5. Shared Field Dictionary by Domain

A file such as `firewall.fields.yml` must be treated as a domain-level normalized dictionary.

Its purpose is to:

- group multiple source field aliases under the same canonical field
- standardize a common vocabulary for a rule family
- reduce duplication during long-term maintenance

Example:

- `src_ip`
- `src`
- `source.ip`

may all map to:

- `canonical.source.ip`

This type of dictionary only defines field mapping relationships; it does not replace the field requirements of an individual rule.

## 6. Metadata Used for Mapping Resolution

Mapping metadata must use the same language as rule metadata instead of introducing a separate mapping vocabulary.

The fields used for resolution are:

- `category`
- `product`
- `service`

Example:

```yaml
logsource:
  category: firewall
  product: any
  service: traffic
```

Application rules:

- matching metadata must follow `rule.logsource.*`
- folder taxonomy remains useful for file organization but does not replace matching metadata
- at the current stage, `domain` is not used as the primary resolution key

## 7. Canonical Field Model

In this project context, a `canonical field` is the repository's internal normalized field set.

Desired properties of a canonical field:

- more stable than the field names currently present in individual tenants
- not directly dependent on vendor raw logs
- not directly dependent on the current parser implementation of a specific SIEM
- small enough to maintain in practice, but explicit enough to preserve a shared semantic contract

A `canonical field` may use OCSF as semantic reference, but it is not required to be a full OCSF implementation at the current stage.

In the current mapping schema, canonical fields may appear in two forms:

- an OCSF-native field reference without the `canonical.` prefix when the field maps directly to OCSF semantics, for example `time`, `src_endpoint.ip`, `http_request.user_agent`, `file.path`, or `malware.name`
- a repository-specific canonical field with the `canonical.` prefix when the project needs an internal name that does not directly match OCSF or intentionally keeps a local extension, for example `canonical.http_request.x_header`

In short:

- use the unprefixed form only for direct and clear OCSF field references
- keep the `canonical.` prefix for repository-specific contracts or when no suitable OCSF field exists

## 8. Scope of Canonicalization

Not every field of a log source needs to be canonicalized at the outset.

At the current stage, canonical fields are created using a detection-driven principle, meaning they are prioritized according to real rule requirements. Priority groups include:

- fields required for a rule to function
- fields used for correlation
- fields used for output, notable generation, or operational review

The corresponding processing model is:

```text
source rule field
  -> canonical field
  -> tenant SIEM field
```

This approach helps:

- reduce initial effort
- avoid the cost of canonicalizing every logsource field up front
- prioritize detection value before expanding the data model

## 9. Operational Rules for Canonical Fields

To avoid uncontrolled growth or semantic duplication, the minimum operating process should be:

1. List the `source rule field` values actually used by a rule.
2. Check whether equivalent canonical fields already exist.
3. Reuse existing canonical fields where possible.
4. Add a new canonical field only when no suitable equivalent exists.
5. Only then map the canonical field to the relevant `tenant SIEM field`.

## 10. `tenants/.../bindings/fields/`

`tenants/.../bindings/fields/` is the tenant-specific implementation layer of field mapping.

Role:

- act as the source of truth for the tenant's actual SIEM fields
- reflect differences by `tenant_id`, `siem_id`, `device_id`, and when necessary `dataset_id`
- provide the final bridge between canonical fields and executable tenant fields

Example:

```text
tenants/
  lab/
    bindings/
      fields/
        checkpoint-fw.fields.yml
```

Such a file may describe:

- which canonical field maps to which SIEM field for the tenant
- which device or dataset the mapping applies to

## 11. Relationship Between Source Rule Field, Canonical Field, OCSF, and Tenant Field

The field layers in the current architecture are separated as follows:

- `source rule field`: a field found in an external rule or legacy content
- `canonical field`: the project's internal normalized field
- `OCSF`: the semantic reference used to design canonical fields
- `tenant SIEM field`: the actual physical field available in the tenant's SIEM

The `canonical field` layer can therefore contain:

- direct OCSF field references
- repository-specific canonical extensions with the `canonical.` prefix

The target pipeline at the current stage is:

```text
source rule field <=> canonical field <=> tenant SIEM field
```

This model is more appropriate for the current project state than assuming a complete end-to-end pipeline from raw logs through parsing, OCSF, and final rendering.

## 12. Role of Hardcoded SPL

In the current project state, hardcoded SPL or SIEM-specific query sections remain valid execution artifacts.

This reflects a controlled architectural decision based on the following conditions:

- a generic converter from standard detection rules to SIEM-specific rules is not yet stable
- the pipeline still requires output that can be reviewed, exported, or deployed
- detection intent and field contracts still need to remain in the normalized layer

Therefore:

- standard detection rules preserve semantic intent and field requirements
- hardcoded SPL acts as a temporary execution artifact
- canonical fields continue to preserve the long-term contract of detection content

## 13. Practical Support Scope in v1.0

During `0.x` or `1.0`, the `mappings/` layer should support the following capabilities:

- map `source rule field` to `canonical field`
- handle field renaming and aliases
- map ingestion targets such as `index` and `sourcetype`
- validate whether a tenant has the fields required to render or use a rule

The following capabilities are not mandatory goals in the same stage:

- deep enum normalization
- automatic type casting
- complex field combination or split logic
- multi-step derived fields
- fully generic field transformation logic

## 14. Current Limitations

At the current stage, the following limitations must be acknowledged explicitly:

- end-to-end mapping from raw logs to final SIEM fields is outside the full control of the `mappings/` layer
- hardcoded SPL remains an important component of the pipeline
- the generic converter has not yet reached the required stability level
- some legacy knowledge about vendor or raw logs is no longer part of the main standard pipeline folders

These limitations must be stated clearly so that the documentation reflects the current operational reality.

## 15. Next Development Direction

Once canonical fields and tenant bindings become more stable, the `mappings/` layer can be expanded in the following directions:

- extend field dictionaries by domain
- add field coverage reports per rule and per tenant
- support simple transforms such as enum aliases or type casts
- progressively standardize field naming on tenant SIEMs
- reassess whether to adopt or build a generic converter

## 16. Conclusion

In the current `SIEM-Detection-as-Code` architecture:

- `mappings/` is the field-contract layer on the detection-content side
- `mappings/detections/` is the standard mapping layer from `source rule field` to `canonical field`
- `tenants/.../bindings/fields/` is the mapping layer from `canonical field` to `tenant SIEM field`
- `canonical field` is the internal standard layer used by detection content
- hardcoded SPL is a valid execution artifact during the transition stage

This document is the normative reference for all changes related to field vocabulary, canonical modeling, mapping resolution, and tenant field binding in the repository.

