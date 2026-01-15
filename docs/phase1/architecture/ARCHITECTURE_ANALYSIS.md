# SIEM Detection - Architecture Analysis & Implementation

**Date**: January 15, 2026  
**Phase**: 1 - Tenant Configuration → SIEM Rule Export

---

## 1. Overview Kiến Trúc

### 1.1 Luồng Dữ Liệu Tổng Quát

```
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: Tenant Config → SIEM Rule Export                              │
└─────────────────────────────────────────────────────────────────────────┘

[1] Tenant Config
    ├── tenant.yaml (tenant_id, name, environment, siem_target)
    ├── logsource.yaml (vendor, product, service config)
    ├── device.yml (device_id, vendor, product, role)
    └── ruleset.yaml (enabled rules)
          ↓
[2] Load & Validate Config
    ├── Load tenant config
    ├── Load device list
    ├── Load logsource definitions
    └── Validate vendor/product mapping
          ↓
[3] Map Rules
    ├── Read detection rules (./rules/detection/**/rule-***.yaml)
    ├── Filter by tenant ruleset
    ├── Filter by logsource compatibility
    └── Extract rule fields & conditions
          ↓
[4] Map Rule Views
    ├── Read rule views (./rule-views/**/rule-view-***.yml)
    ├── Map rule.field → ocsf.field
    └── Extract output fields mapping
          ↓
[5] Map Logsource Registry
    ├── Read mapping registry (./logsource-mapping-registry/**/mapping.yml)
    ├── Map ocsf.field → vendor.siem_field
    ├── Get field conversion rules
    └── Extract query parameters
          ↓
[6] Generate SIEM Rule
    ├── Combine rule logic + field mappings
    ├── Generate vendor-specific syntax
    ├── Build correlation queries
    └── Add SIEM metadata (index, sourcetype, etc)
          ↓
[7] Export to siem-rule.json
    ├── Export rules in JSON format
    ├── Include field mappings
    ├── Add deployment metadata
    └── Generate deployment package
```

### 1.2 Key Components & Roles

| Component | File/Folder | Role | Input | Output |
|-----------|-------------|------|-------|--------|
| **Tenant Config Loader** | `tenant-manager/` | Load tenant, device, logsource config | YAML files | Dict of config |
| **Rule Loader** | `rules/detection/` | Load detection rules | Rule YAML | Dict of rules |
| **Rule View Mapper** | `rule-views/` | Map rule field → ocsf field | Rule-view YAML | Field mapping dict |
| **Logsource Mapper** | `logsource-mapping-registry/` | Map ocsf field → siem field | Mapping YAML | Field conversion dict |
| **Rule Generator** | - | Combine all mappings | All dicts | SIEM rule syntax |
| **Export Engine** | - | Export to siem-rule.json | SIEM rules | JSON file |

---

## 2. Data Structure Analysis

### 2.1 Tenant Config Schema

```yaml
# tenant.yaml
tenant_id: tenant-a
name: Company A
environment: production
timezone: Asia/Ho_Chi_Minh
siem_target: splunk
```

### 2.2 Device Configuration Schema

```yaml
# device.yml
- device_id: fg-hq-01
  vendor: checkpoint
  product: checkpoint
  role: firewall
  location: hq
  enabled: true
```

### 2.3 Logsource Configuration Schema

```yaml
# logsource.yaml
- vendor: checkpoint
  product: checkpoint
  service: traffic
  enabled: true
```

### 2.4 Detection Rule Schema

```yaml
# rules/detection/network/firewall/base/net_fw_.yml
title: Outbound connection in port 135
name: fw_outbound_connection_port_135
id: 2a129a58-7725-48c9-8b3a-0a2264522a68
status: test
description: ...
logsource:
    category: firewall
    product: any
    service: traffic
detection:
    selection_port:
        dst_port: 135
    selection_protocol:
        protocol: [tcp, 6]
    condition: selection_port and selection_protocol and ...
fields:
    - _time
    - src_ip
    - dest_ip
    - action
```

### 2.5 Rule View Mapping Schema

```yaml
# rule-views/network/firewall/base/rule-view-firewall-any-traffic.yml
logsource:
    category: firewall
    product: any
    service: traffic
mapping:
    _time: ocsf.event.time
    src_ip: ocsf.source.ip
    src_port: ocsf.source.port
    dest_ip: ocsf.destination.ip
    dest_port: ocsf.destination.port
    action: ocsf.event.action
    firewall_policy_name: ocsf.firewall.policy.name
    protocol: ocsf.network.protocol
    event_count: ocsf.event.count
```

### 2.6 Logsource Mapping Registry Schema

```yaml
# logsource-mapping-registry/vendor/checkpoint/checkpoint-traffic-convert-field.yml
logsource:
    vendor: checkpoint
    product: vpn-1_firewall-1
    service: traffic

# Raw field → SIEM field mapping
siem_fields-map-to-raw_fields:
    _time: time
    src_ip: src
    dest_ip: dst
    protocol: proto

# SIEM field → OCSF field mapping
siem_fields:
    _time: ocsf.event.time
    src_ip: ocsf.source.ip
    dest_ip: ocsf.destination.ip
    proto: ocsf.network.protocol
```

---

## 3. Processing Logic - Function Architecture

### 3.1 Function Hierarchy

```
Main Orchestrator
├── load_tenant_config()
│   ├── load_yaml_file()
│   ├── validate_config_schema()
│   └── merge_configs()
│
├── load_rules()
│   ├── find_rule_files()
│   ├── parse_rule()
│   ├── filter_by_ruleset()
│   └── filter_by_logsource()
│
├── load_rule_views()
│   ├── find_rule_view_files()
│   ├── parse_rule_view()
│   └── match_logsource()
│
├── load_logsource_mappings()
│   ├── find_mapping_files()
│   ├── parse_mapping()
│   └── match_vendor_product()
│
├── build_field_mappings()
│   ├── combine_rule_field_mapping()      # rule field → ocsf field
│   ├── combine_ocsf_siem_mapping()       # ocsf field → siem field
│   └── build_full_chain_mapping()        # rule field → siem field
│
├── generate_siem_rule()
│   ├── translate_conditions()
│   ├── translate_fields()
│   ├── generate_vendor_syntax()
│   └── add_metadata()
│
└── export_to_json()
    ├── serialize_rules()
    ├── serialize_mappings()
    └── write_json_file()
```

### 3.2 Processing Sequence

```
1. Load Phase
   - Tenant config (1 file)
   - Device list (1 file)
   - Logsource config (1 file)
   - Ruleset (optional, 1 file)

2. Validation Phase
   - Validate schema compliance
   - Check vendor/product compatibility
   - Validate logsource definitions

3. Selection Phase
   - Filter rules by ruleset (if provided)
   - Filter rules by logsource compatibility
   - Filter logsource configs by enabled=true

4. Mapping Phase
   - Load applicable rule views (by logsource category/product/service)
   - Load applicable logsource mappings (by vendor/product/service)
   - Build field mapping chains

5. Generation Phase
   - Generate SIEM rule syntax (vendor-specific)
   - Apply field translations
   - Build queries with proper syntax

6. Export Phase
   - Serialize to JSON format
   - Include metadata and mappings
   - Output siem-rule.json
```

---

## 4. Field Mapping Chain Example

### 4.1 Complete Mapping Flow

```
Detection Rule Field
    ↓
Rule View Mapping (rule field → ocsf field)
    ↓
OCSF Normalized Field
    ↓
Logsource Mapping (ocsf field → siem field)
    ↓
SIEM-specific Field (Splunk/ELK/QRadar)
    ↓
Query Generator
```

### 4.2 Concrete Example: src_ip

```
Detection Rule (net_fw_.yml)
    field: src_ip
    ↓ (Rule View)
    ocsf.source.ip
    ↓ (Logsource Mapping - Checkpoint)
    src (raw checkpoint field)
    ↓ (Splunk Config)
    field: src in Splunk query

Complete Chain:
net_fw_.yml: src_ip
    → rule-view-firewall-any-traffic.yml: ocsf.source.ip
    → checkpoint-traffic-convert-field.yml: src
    → Splunk: sourcetype=checkpoint src=<value>
```

### 4.3 Mapping Files Relationship

```
rule-views/network/firewall/base/rule-view-firewall-any-traffic.yml
    ├── Covers: logsource(category=firewall, product=any, service=traffic)
    ├── Maps: rule fields → ocsf fields
    └── Output: {_time, src_ip, dest_ip, action, ...} → {ocsf.event.time, ocsf.source.ip, ...}

logsource-mapping-registry/vendor/checkpoint/checkpoint-traffic-convert-field.yml
    ├── Covers: logsource(vendor=checkpoint, product=vpn-1_firewall-1, service=traffic)
    ├── Has 2 mappings:
    │   1. siem_fields-map-to-raw_fields: siem field → raw checkpoint field
    │   2. siem_fields: siem field → ocsf field
    └── Can be used bidirectionally
```

---

## 5. Proposed Function Design

### 5.1 Core Loader Functions (Role: Data Loading)

```python
def load_yaml_file(file_path: str) -> Dict[str, Any]
def load_tenant_config(tenant_path: str) -> Dict[str, Any]
def load_device_list(device_file: str) -> List[Dict[str, Any]]
def load_logsource_config(logsource_file: str) -> List[Dict[str, Any]]
def load_rules(rules_dir: str, filters: Dict = None) -> List[Dict[str, Any]]
```

### 5.2 Validation Functions (Role: Data Validation)

```python
def validate_tenant_config(config: Dict) -> bool
def validate_logsource_config(logsources: List[Dict]) -> bool
def validate_rule(rule: Dict) -> bool
def validate_rule_view(rule_view: Dict) -> bool
def validate_mapping(mapping: Dict) -> bool
```

### 5.3 Filtering Functions (Role: Filtering & Selection)

```python
def filter_rules_by_ruleset(rules: List, ruleset: List[str]) -> List
def filter_rules_by_logsource(rules: List, logsources: List[Dict]) -> List
def match_logsource(rule_logsource: Dict, config_logsources: List[Dict]) -> List[Dict]
def find_applicable_rule_views(logsource: Dict, rule_views_dir: str) -> List[Dict]
def find_applicable_mappings(vendor: str, product: str, service: str, mappings_dir: str) -> List[Dict]
```

### 5.4 Mapping Functions (Role: Field Mapping)

```python
def build_rule_to_ocsf_mapping(rule_view: Dict) -> Dict[str, str]
def build_ocsf_to_siem_mapping(mapping: Dict) -> Dict[str, str]
def build_full_field_chain(rule_field: str, rule_view: Dict, mapping: Dict) -> str
def merge_field_mappings(mappings: List[Dict[str, str]]) -> Dict[str, str]
```

### 5.5 Translation Functions (Role: Syntax Generation)

```python
def translate_conditions(rule_detection: Dict, mappings: Dict) -> str
def translate_field(field_name: str, mappings: Dict) -> str
def generate_splunk_query(rule: Dict, mappings: Dict) -> str
def generate_elk_query(rule: Dict, mappings: Dict) -> str
def add_siem_metadata(rule: Dict, tenant: Dict) -> Dict
```

### 5.6 Export Functions (Role: Output Generation)

```python
def generate_siem_rule(rule: Dict, mappings: Dict, tenant: Dict) -> Dict
def export_rules_to_json(rules: List[Dict], output_file: str) -> None
def serialize_with_metadata(rules: List, mappings: Dict, tenant: Dict) -> Dict
```

### 5.7 Orchestration Function (Role: Process Control)

```python
def generate_siem_deployment_package(tenant_path: str, output_file: str) -> None
```

---

## 6. Error Handling & Validation Strategy

```
Load Phase Errors:
├── File not found
├── Invalid YAML syntax
└── Missing required fields

Validation Phase Errors:
├── Schema mismatch
├── Unsupported vendor/product
├── Logsource incompatibility
└── Missing field mappings

Processing Phase Errors:
├── No matching rule views
├── No matching logsource mappings
├── Field translation failures
└── Condition parsing errors

Recovery Strategy:
├── Log all errors with context
├── Continue with valid rules (warn on invalid)
├── Generate partial output if possible
└── Provide detailed error report
```

---

## 7. Configuration File Structure

### 7.1 Tenant Manager

```
tenant-manager/
├── tenants/
│   └── tenant-A/
│       ├── tenant.yaml              # Tenant metadata
│       ├── device.yml               # Device list
│       ├── logsource.yaml           # Logsource enablement
│       ├── ruleset.yaml             # Enabled rules (optional)
│       ├── capabilities.yaml        # SIEM capabilities
│       └── versions.yaml            # Config versions
└── schemas/
    ├── tenant.schema.yaml
    ├── device.schema.yaml
    ├── logsource.schema.yaml
    └── ruleset.schema.yaml
```

### 7.2 Mapping Dependencies

```
rules/detection/
    └── network/firewall/base/
        └── net_fw_.yml
            ├── Fields: src_ip, dest_ip, action, ...
            ├── Logsource: category=firewall, product=any
            └── Status: test/production

        ↓ needs ↓

rule-views/network/firewall/base/
    └── rule-view-firewall-any-traffic.yml
        ├── Covers: logsource(category=firewall, product=any, service=traffic)
        ├── Maps: src_ip→ocsf.source.ip, dest_ip→ocsf.destination.ip
        └── Output: {ocsf.event.time, ocsf.source.ip, ...}

        ↓ needs ↓

logsource-mapping-registry/vendor/checkpoint/
    ├── checkpoint-traffic-convert-field.yml
    │   ├── Covers: logsource(vendor=checkpoint, product=vpn-1_firewall-1, service=traffic)
    │   ├── Map 1: src_ip→src (raw field)
    │   └── Map 2: src_ip→ocsf.source.ip (normalized)
    └── checkpoint-splunk-conf.yml
        ├── Splunk config: index, sourcetype
        └── Filter metadata
```

