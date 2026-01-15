# CheckPoint Logsource Mapping

## Overview

Cấu trúc mapping cho CheckPoint firewall và VPN traffic logs.

## 📁 File Structure

```
checkpoint/
├── traffic-convert-field.yaml        # Raw field → SIEM field conversion
├── checkpoint-traffic-mapping.yaml   # SIEM field → OCSF field mapping
├── checkpoint-splunk-conf.yaml       # Splunk configuration
├── checkpoint-log-knowledge.yaml     # Extended knowledge base (empty)
└── README.md                         # This file
```

## 🔄 Mapping Flow

```
Checkpoint Raw Log
    ↓
    ├─→ traffic-convert-field.yaml (raw_field → siem_field)
    ↓
SIEM Fields (normalized)
    ↓
    ├─→ checkpoint-traffic-mapping.yaml (siem_field → ocsf_field)
    ↓
OCSF Normalized Fields
```

## 📄 File Descriptions

### traffic-convert-field.yaml (3.3 KB)

**Purpose**: Convert raw CheckPoint fields to standardized SIEM fields

**Sections**:
- `logsource`: Defines log source identification
  - category: firewall
  - vendor: checkpoint
  - product: vpn-1_firewall-1
  - service: traffic

- `siem_fields-map-to-raw_fields`: Map SIEM fields to raw log fields
  - Example: `_time: time`, `src_ip: src`, `dest_ip: dst`

- `siem_fields`: Map SIEM fields to OCSF standard
  - Example: `src_ip: ocsf.source.ip`, `dest_ip: ocsf.destination.ip`

**Example Raw Field**:
```
action:"Accept"; src:"10.16.96.193"; s_port:"61272"; 
dst:"40.126.35.153"; service:"443"; proto:"6"
```

**Conversion**:
```
Raw Field               SIEM Field         OCSF Field
action                 action             ocsf.event.action
src                    src_ip             ocsf.source.ip
s_port                 s_port             ocsf.source.port
dst                    dest_ip            ocsf.destination.ip
service                service            ocsf.destination.port
proto                  proto              ocsf.network.protocol
```

### checkpoint-traffic-mapping.yaml (3.0 KB)

**Purpose**: Map SIEM fields to OCSF standard format

**Sections**:
- `logsource`: Log source identification
- `field_categories`: Categorized list of field types
  - event, network, policy, zones, vpn

- `mapping`: SIEM field → OCSF field mapping
  - References `traffic-convert-field.yaml` for raw field conversion
  - Applies OCSF normalization

**Conversion Chain Reference**:
```yaml
conversion_chain:
  - raw_fields: from checkpoint vpn-1_firewall-1 logs
  - siem_fields: defined in traffic-convert-field.yaml
  - ocsf_fields: defined in checkpoint-traffic-mapping.yaml mapping section
```

### checkpoint-splunk-conf.yaml (44 bytes)

**Purpose**: Splunk-specific configuration

**Contents**:
```yaml
config:
  index: checkpoint
  sourcetype: 
```

### checkpoint-log-knowledge.yaml (empty)

**Purpose**: Extended knowledge base for field enrichment (future use)

---

## 📝 Field Reference

### Common Fields in CheckPoint Logs

| SIEM Field | Raw Field | OCSF Field | Example |
|------------|-----------|-----------|---------|
| _time | time | ocsf.event.time | 1768215240 |
| src_ip | src | ocsf.source.ip | 10.16.96.193 |
| s_port | s_port | ocsf.source.port | 61272 |
| dest_ip | dst | ocsf.destination.ip | 40.126.35.153 |
| service | service | ocsf.destination.port | 443 |
| security_inzone | security_inzone | ocsf.source.zone | Internal_IT_Zone |
| security_outzone | security_outzone | ocsf.destination.zone | ExternalZone |
| action | action | ocsf.event.action | Accept |
| rule_name | rule_name | ocsf.firewall.policy.name | IT Network Access Internet |
| proto | proto | ocsf.network.protocol | 6 (TCP) |

---

## 🔍 How to Use

### For Rule Detection

1. Load `traffic-convert-field.yaml`
2. Parse raw CheckPoint logs using `siem_fields-map-to-raw_fields` section
3. Get normalized SIEM fields

### For SIEM Translation

1. Use SIEM fields from step above
2. Load `checkpoint-traffic-mapping.yaml`
3. Map to OCSF fields using `mapping` section
4. Generate SIEM-specific rules (Splunk, ELK, QRadar)

### For Splunk Configuration

1. Use settings from `checkpoint-splunk-conf.yaml`
2. Apply to Splunk configuration
3. Process CheckPoint logs

---

## ✅ Status

- ✅ Raw field → SIEM field mapping: Complete (traffic-convert-field.yaml)
- ✅ SIEM field → OCSF mapping: Complete (checkpoint-traffic-mapping.yaml)
- ✅ Splunk configuration: Defined (checkpoint-splunk-conf.yaml)
- ⏳ Extended knowledge base: Planned (checkpoint-log-knowledge.yaml)

---

## 📌 Notes

- All files use `.yaml` extension for consistency
- Current implementation is demo/test phase
- Missing files (checkpoint-log-knowledge.yaml) can be added as needed
- Field mapping is centralized in convert-field.yaml to avoid duplication
- References between files ensure maintainability

---

**Last Updated**: January 15, 2026
