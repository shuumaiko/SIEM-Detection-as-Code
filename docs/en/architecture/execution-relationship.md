# Execution Component Architecture

> Vietnamese source: [execution-relationship.md](../../architecture/execution-relationship.md)

## 1. Purpose

`execution/` is the SIEM execution-configuration layer. This layer does not define detection intent. Instead, it defines how a semantic rule is operated on a specific SIEM.

## 2. Role

`execution/` is used to store:

- schedules such as `cron`, `earliest`, and `latest`
- notable metadata such as `enabled`, `severity`, and `risk_score`
- default policy per SIEM
- per-rule execution overrides

In the current stage of the repository, this layer is most explicit under `execution/splunk/`.

## 3. Current Structure

```text
execution/
  splunk/
    defaults.yaml
    rule-overrides.yaml
    legacy/
      ...
```

Meaning:

- `defaults.yaml`: the default Splunk execution policy
- `rule-overrides.yaml`: execution exceptions keyed by `rule_id`
- `legacy/`: transition-stage execution artifacts or files retained from the older model

## 4. Relationship to Rules and Tenants

`execution/` is a shared SIEM layer, not tenant-specific configuration.

When rendering a rule, execution configuration is resolved in this order:

1. `execution/<siem>/defaults.yaml`
2. `execution/<siem>/rule-overrides.yaml`
3. `tenants/<tenant>/overrides/execution/...`

In short:

```text
execution defaults
  <= rule-specific execution override
  <= tenant-specific execution override
```

## 5. Relationship to Hardcoded Queries

In the current transition stage, hardcoded queries or hardcoded SPL remain valid execution artifacts. However:

- a hardcoded query does not replace the semantic rule
- a hardcoded query does not replace execution metadata
- `execution/` remains the dedicated layer for schedules, notable settings, severity, and risk score

In short:

- the query answers what logic runs on the SIEM
- execution answers how that rule is operated on the SIEM

## 6. Relationship to Tenant Overrides

Tenant overrides are the final tuning layer and are separated under:

```text
tenants/
  <tenant>/
    overrides/
      execution/
        <siem>/
          ...
```

The role of a tenant execution override is to:

- adjust cron schedules for a specific tenant
- adjust severity or risk score for an operational context
- adjust notable behavior without changing the rule's shared execution configuration

## 7. Conclusion

In the current architecture:

- `execution/` is the SIEM execution-configuration layer
- `execution/` does not replace semantic rules
- `execution/` does not replace tenant overrides
- `execution/` is input configuration, not output artifact

This document is the normative reference for changes related to default execution policy, rule-specific execution overrides, and tenant-specific execution tuning.
