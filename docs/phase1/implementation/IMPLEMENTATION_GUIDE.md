# SIEM Detection - Phase 1 Implementation Guide

## Document Overview

This guide provides:
1. **Detailed function specifications** for each processing stage
2. **Data flow examples** with real data
3. **Error handling strategies**
4. **Testing approach**
5. **Implementation roadmap**

---

## Part 1: Function Specifications

### Group 1: Loaders (Data Loading)

#### 1.1 `load_yaml_file(file_path: str) -> Dict`

**Purpose**: Base YAML file loader

**Input**: File path (absolute or relative)

**Output**: Parsed YAML content as dictionary

**Process Flow**:
```
file_path → exists? → read file → parse YAML → return dict
                ↓              ↓
              error        error
```

**Error Cases**:
- File not found → FileNotFoundError
- Invalid YAML syntax → yaml.YAMLError
- Empty file → return {}

**Example**:
```python
config = load_yaml_file('./tenant-manager/tenants/tenant-A/tenant.yaml')
# Output:
# {
#     'tenant_id': 'tenant-a',
#     'name': 'Company A',
#     'environment': 'production',
#     'timezone': 'Asia/Ho_Chi_Minh',
#     'siem_target': 'splunk'
# }
```

---

#### 1.2 `load_tenant_config(tenant_base_path: str) -> Dict`

**Purpose**: Load complete tenant configuration (composite loader)

**Input**: Base path to tenant directory

**Output**: Dictionary with keys: tenant, devices, logsources, ruleset

**Process Flow**:
```
tenant_path
    ├─ load tenant.yaml → tenant dict
    ├─ load device.yml → devices list
    ├─ load logsource.yaml → logsources list
    └─ load ruleset.yaml (optional) → ruleset list
         ↓
    Combine into single config dict
```

**Data Structure Output**:
```python
{
    'tenant': {...},
    'devices': [...],
    'logsources': [...],
    'ruleset': [...]  # or empty list if not exists
}
```

**Example Output**:
```python
config = load_tenant_config('./tenant-manager/tenants/tenant-A')
# config['tenant']:
{
    'tenant_id': 'tenant-a',
    'name': 'Company A',
    'environment': 'production',
    'timezone': 'Asia/Ho_Chi_Minh',
    'siem_target': 'splunk'
}

# config['devices']:
[
    {
        'device_id': 'fg-hq-01',
        'vendor': 'checkpoint',
        'product': 'checkpoint',
        'role': 'firewall',
        'location': 'hq'
    },
    {
        'device_id': 'fg-branch-01',
        'vendor': 'fortinet',
        'product': 'fortigate',
        'role': 'firewall',
        'location': 'branch office'
    }
]

# config['logsources']:
[
    {
        'vendor': 'checkpoint',
        'product': 'checkpoint',
        'service': 'traffic',
        'enabled': True
    },
    {
        'vendor': 'fortinet',
        'product': 'fortigate',
        'service': 'traffic',
        'enabled': True
    }
]
```

---

#### 1.3 `load_rules(rules_dir: str, category: Optional[str]) -> List[Dict]`

**Purpose**: Load all detection rules

**Input**: 
- rules_dir: Path to rules directory
- category: Optional filter (e.g., 'network')

**Output**: List of rule dictionaries

**Process Flow**:
```
rules_dir
    ├─ Walk directory tree
    ├─ Find rule-*.yml files
    ├─ Parse each file
    ├─ Handle multi-document YAML (---)
    └─ Collect into list

Handle errors:
    └─ Failed to load → warn + continue
```

**Example Output**:
```python
rules = load_rules('./rules/detection')
# [
#     {
#         'title': 'Outbound connection in port 135',
#         'name': 'fw_outbound_connection_port_135',
#         'id': '2a129a58-7725-48c9-8b3a-0a2264522a68',
#         'status': 'test',
#         'logsource': {
#             'category': 'firewall',
#             'product': 'any',
#             'service': 'traffic'
#         },
#         'detection': {...},
#         'fields': [...]
#     },
#     ...
# ]
```

---

#### 1.4 `load_rule_views(rule_views_dir: str) -> List[Dict]`

**Purpose**: Load rule view definitions

**Input**: Path to rule-views directory

**Output**: List of rule view dictionaries

**Structure**:
```
rule_views_dir
    ├─ network/firewall/base/
    │   └─ rule-view-firewall-any-traffic.yml
    ├─ network/dns/base/
    │   └─ rule-view-dns-*.yml
    └─ ...
```

**Example Output**:
```python
rule_views = load_rule_views('./rule-views')
# [
#     {
#         'logsource': {
#             'category': 'firewall',
#             'product': 'any',
#             'service': 'traffic'
#         },
#         'mapping': {
#             '_time': 'ocsf.event.time',
#             'src_ip': 'ocsf.source.ip',
#             'dest_ip': 'ocsf.destination.ip',
#             'action': 'ocsf.event.action',
#             ...
#         }
#     },
#     ...
# ]
```

---

#### 1.5 `load_logsource_mappings(mappings_dir: str) -> List[Dict]`

**Purpose**: Load logsource mapping definitions

**Input**: Path to logsource-mapping-registry directory

**Output**: List of mapping dictionaries

**Structure**:
```
mappings_dir
    ├─ vendor/checkpoint/
    │   ├─ checkpoint-traffic-mapping.yml
    │   ├─ checkpoint-traffic-convert-field.yml
    │   └─ checkpoint-splunk-conf.yml
    ├─ vendor/fortinet/
    │   └─ fortigate/
    │       ├─ mapping.yaml
    │       └─ ...
    └─ ...
```

**Example Output**:
```python
mappings = load_logsource_mappings('./logsource-mapping-registry')
# [
#     {
#         'logsource': {
#             'category': 'firewall',
#             'vendor': 'checkpoint',
#             'product': 'vpn-1_firewall-1',
#             'service': 'traffic'
#         },
#         'siem_fields-map-to-raw_fields': {
#             '_time': 'time',
#             'src_ip': 'src',
#             'dest_ip': 'dst',
#             ...
#         },
#         'siem_fields': {
#             '_time': 'ocsf.event.time',
#             'src_ip': 'ocsf.source.ip',
#             'dest_ip': 'ocsf.destination.ip',
#             ...
#         }
#     },
#     ...
# ]
```

---

### Group 2: Validators (Data Validation)

#### 2.1 `validate_logsource_match(rule_logsource, config_logsource) -> bool`

**Purpose**: Check if rule logsource matches tenant's logsource config

**Input**:
- rule_logsource: From detection rule (uses 'any' as wildcard)
- config_logsource: From tenant config (specific vendor/product)

**Output**: True if matches, False otherwise

**Matching Logic**:
```
Rule: category=firewall, product=any, service=traffic
Config: vendor=checkpoint, product=checkpoint, service=traffic
                                          ↓
Is rule_product 'any'? → YES → Match by category + service
Is rule_product specific? → NO → Must match all fields
```

**Example**:
```python
rule_logsource = {
    'category': 'firewall',
    'product': 'any',
    'service': 'traffic'
}

config_logsource_1 = {
    'vendor': 'checkpoint',
    'product': 'checkpoint',
    'service': 'traffic',
    'enabled': True
}

config_logsource_2 = {
    'vendor': 'fortinet',
    'product': 'fortigate',
    'service': 'traffic',
    'enabled': True
}

result1 = validate_logsource_match(rule_logsource, config_logsource_1)  # True
result2 = validate_logsource_match(rule_logsource, config_logsource_2)  # True
```

---

#### 2.2 `validate_rule(rule: Dict) -> Tuple[bool, List[str]]`

**Purpose**: Validate rule structure

**Checks**:
- [ ] Has title
- [ ] Has name (unique identifier)
- [ ] Has id (UUID)
- [ ] Has logsource with category
- [ ] Has detection with condition

**Example**:
```python
rule = {
    'title': 'Outbound connection in port 135',
    'name': 'fw_outbound_connection_port_135',
    'id': '2a129a58-7725-48c9-8b3a-0a2264522a68',
    'logsource': {
        'category': 'firewall',
        'product': 'any',
        'service': 'traffic'
    },
    'detection': {
        'selection_port': {'dst_port': 135},
        'condition': 'selection_port'
    }
}

is_valid, errors = validate_rule(rule)
# is_valid: True
# errors: []
```

---

### Group 3: Filters & Selectors

#### 3.1 `filter_rules_by_logsource(rules, logsources) -> List[Dict]`

**Purpose**: Filter rules to only those compatible with tenant's logsources

**Algorithm**:
```
For each rule:
    For each tenant_logsource:
        If logsource_match(rule, tenant_logsource) AND enabled:
            Add to filtered_rules
            Break (skip other logsources for this rule)
```

**Example**:
```python
# Tenant has 2 logsources: checkpoint+traffic, fortinet+traffic
# Rules directory has 20 rules
# Only 8 rules match firewall category
# Filter returns those 8 rules

filtered = filter_rules_by_logsource(
    all_rules=[20 rules],
    logsources=[checkpoint/traffic, fortinet/traffic]
)
# len(filtered) = 8
```

---

#### 3.2 `find_matching_rule_view(rule_logsource, rule_views) -> Optional[Dict]`

**Purpose**: Find rule view that applies to a rule's logsource

**Logic**:
```
rule_view matches rule if:
    view.logsource.category == rule.logsource.category
    AND (view.logsource.product == 'any' OR view.logsource.product == rule.logsource.product)
    AND view.logsource.service == rule.logsource.service
```

**Example**:
```python
rule_logsource = {
    'category': 'firewall',
    'product': 'any',
    'service': 'traffic'
}

rule_views = [
    # View 1: Matches!
    {
        'logsource': {
            'category': 'firewall',
            'product': 'any',
            'service': 'traffic'
        },
        'mapping': {...}
    },
    # View 2: No match (wrong service)
    {
        'logsource': {
            'category': 'firewall',
            'product': 'any',
            'service': 'vpn'
        },
        'mapping': {...}
    }
]

matched_view = find_matching_rule_view(rule_logsource, rule_views)
# Returns View 1
```

---

#### 3.3 `find_matching_logsource_mapping(vendor, product, service, mappings) -> Optional[Dict]`

**Purpose**: Find logsource mapping for vendor/product/service

**Logic**:
```
mapping matches if:
    mapping.logsource.vendor == vendor
    AND mapping.logsource.product == product
    AND mapping.logsource.service == service
```

**Example**:
```python
matched = find_matching_logsource_mapping(
    vendor='checkpoint',
    product='vpn-1_firewall-1',
    service='traffic',
    mappings=[...]
)
# Returns checkpoint-traffic-convert-field.yml data
```

---

### Group 4: Field Mappers

#### 4.1 `build_rule_to_ocsf_mapping(rule_view) -> Dict[str, str]`

**Purpose**: Extract field mapping from rule view

**Input**:
```yaml
mapping:
    _time: ocsf.event.time
    src_ip: ocsf.source.ip
    dest_ip: ocsf.destination.ip
```

**Output**:
```python
{
    '_time': 'ocsf.event.time',
    'src_ip': 'ocsf.source.ip',
    'dest_ip': 'ocsf.destination.ip'
}
```

---

#### 4.2 `build_ocsf_to_siem_mapping(logsource_mapping) -> Dict[str, str]`

**Purpose**: Extract and reverse OCSF→SIEM mapping

**Input**:
```yaml
siem_fields:
    _time: ocsf.event.time
    src_ip: ocsf.source.ip
```

**Process**: Reverse mapping (ocsf → siem_field)

**Output**:
```python
{
    'ocsf.event.time': '_time',
    'ocsf.source.ip': 'src_ip'
}
```

---

#### 4.3 `build_full_field_chain(rule_field, rule_view, ocsf_to_siem) -> Optional[str]`

**Purpose**: Complete field mapping chain

**Flow**:
```
rule_field (src_ip)
    ↓ via rule_view mapping
ocsf_field (ocsf.source.ip)
    ↓ via ocsf_to_siem mapping
siem_field (src)
```

**Example**:
```python
chain = build_full_field_chain(
    rule_field='src_ip',
    rule_view={
        'mapping': {
            'src_ip': 'ocsf.source.ip'
        }
    },
    ocsf_to_siem={
        'ocsf.source.ip': 'src'
    }
)
# Output: 'src'
```

---

#### 4.4 `build_rule_field_mappings(rule, rule_view, ocsf_to_siem, siem_to_raw) -> Dict`

**Purpose**: Build complete field mapping table for a rule

**Output Structure**:
```python
{
    'src_ip': {
        'rule_field': 'src_ip',
        'ocsf_field': 'ocsf.source.ip',
        'siem_field': 'src',
        'raw_field': 'src'  # native vendor field name
    },
    'dest_ip': {...},
    ...
}
```

---

### Group 5: Translators (Syntax Generation)

#### 5.1 `generate_splunk_rule(rule, field_mappings, tenant) -> Dict`

**Purpose**: Generate Splunk-specific rule format

**Output**:
```python
{
    'name': 'fw_outbound_connection_port_135',
    'title': 'Outbound connection in port 135',
    'description': '...',
    'search': 'sourcetype=checkpoint ...',
    'detection': {...},
    'output_fields': ['src', 'dst', 'action', ...],
    'tags': ['attack.initial-access', ...],
    'status': 'test',
    'tenant_id': 'tenant-a',
    'device_id': 'fg-hq-01',
    'device_role': 'firewall'
}
```

---

#### 5.2 `generate_elk_rule(rule, field_mappings, tenant) -> Dict`

**Purpose**: Generate Elasticsearch query format

**Output**:
```python
{
    'rule': {
        'id': '2a129a58-7725-48c9-8b3a-0a2264522a68',
        'name': 'Outbound connection in port 135',
        'description': '...',
        'query': {
            'bool': {
                'must': [
                    {'match': {'src_ip': '...'}},
                    {'match': {'dest_port': 135}}
                ]
            }
        },
        'enabled': True,
        'tags': [...]
    }
}
```

---

### Group 6: Export Functions

#### 6.1 `export_rules_to_json(rules, field_mappings_list, tenant, output_file)`

**Purpose**: Export generated rules to siem-rule.json

**Output File Structure**:
```json
{
    "metadata": {
        "tenant_id": "tenant-a",
        "tenant_name": "Company A",
        "environment": "production",
        "siem_target": "splunk",
        "export_timestamp": "2026-01-15T10:30:00",
        "version": "1.0"
    },
    "rules": [
        {...rule1...},
        {...rule2...}
    ],
    "field_mappings": [
        {...mappings1...},
        {...mappings2...}
    ],
    "total_rules": 15
}
```

---

### Group 7: Orchestration

#### 7.1 `process_tenant_to_siem_rules(tenant_path, rules_dir, rule_views_dir, mappings_dir, output_file, siem_type)`

**Purpose**: Main orchestration function

**Steps**:
```
1. Load tenant config
2. Load rules + reference data
3. Filter rules by logsource
4. Build field mappings
5. Generate SIEM-specific rules
6. Export to JSON

Each step has error handling + progress reporting
```

**Example Execution**:
```
[1/6] Loading tenant configuration...
  ✓ Tenant: Company A (tenant-a)
  ✓ SIEM Target: splunk
  ✓ Devices: 2
  ✓ Logsources: 2

[2/6] Loading detection rules and reference data...
  ✓ Rules loaded: 20
  ✓ Rule views loaded: 5
  ✓ Logsource mappings loaded: 12

[3/6] Filtering rules by logsource compatibility...
  ✓ Compatible rules: 8

[4/6] Building field mappings...
  ✓ Generated 16 SIEM rules (8 rules × 2 devices)

[5/6] Exporting rules to JSON...
  ✓ Exported 16 rules to ./siem-rule.json

[6/6] Process complete!
======================================================================
Summary:
  Total rules loaded: 20
  Compatible rules: 8
  SIEM rules generated: 16
  Output file: ./siem-rule.json
======================================================================
```

---

## Part 2: Error Handling Strategy

### Error Types & Recovery

```
LOAD PHASE
├── FileNotFoundError
│   ├── Message: "File not found: <path>"
│   └── Recovery: Exit with error (required file)
├── yaml.YAMLError
│   ├── Message: "Invalid YAML in <file>: <details>"
│   └── Recovery: Exit with error (data structure issue)
└── TypeError
    ├── Message: "Expected list, got dict"
    └── Recovery: Wrap single item in list

VALIDATION PHASE
├── SchemaMismatch
│   ├── Message: "Missing required field: <field>"
│   └── Recovery: Warn + skip rule
├── IncompatibleLogsource
│   ├── Message: "No rule view found for..."
│   └── Recovery: Warn + skip rule
└── MissingMapping
    ├── Message: "No mapping found for vendor/product/service"
    └── Recovery: Warn + skip (continue with other devices)

GENERATION PHASE
├── FieldMappingFailed
│   ├── Message: "Field <field> not mapped"
│   └── Recovery: Skip field + continue
└── ConditionParsingFailed
    ├── Message: "Cannot parse condition: <condition>"
    └── Recovery: Use raw condition + warn

EXPORT PHASE
├── IOError
│   ├── Message: "Cannot write to <file>"
│   └── Recovery: Retry or use alternate path
└── SerializationFailed
    ├── Message: "Cannot serialize object"
    └── Recovery: Remove problematic field + warn
```

---

## Part 3: Testing Approach

### Unit Test Example

```python
def test_filter_rules_by_logsource():
    """Test rule filtering by logsource"""
    
    rules = [
        {
            'name': 'firewall_rule',
            'logsource': {
                'category': 'firewall',
                'product': 'any',
                'service': 'traffic'
            }
        },
        {
            'name': 'endpoint_rule',
            'logsource': {
                'category': 'endpoint',
                'product': 'any',
                'service': 'process'
            }
        }
    ]
    
    logsources = [
        {
            'vendor': 'checkpoint',
            'product': 'checkpoint',
            'service': 'traffic',
            'enabled': True
        }
    ]
    
    filtered = filter_rules_by_logsource(rules, logsources)
    
    assert len(filtered) == 1
    assert filtered[0]['name'] == 'firewall_rule'
```

---

## Part 4: Implementation Roadmap

### Phase 1a: Core Loaders (Week 1)
- [ ] `load_yaml_file()` - Basic YAML loading
- [ ] `load_tenant_config()` - Composite loader
- [ ] `load_rules()` - Multi-file rule loading
- [ ] `load_rule_views()` - Rule view loading
- [ ] `load_logsource_mappings()` - Mapping loading

### Phase 1b: Validators (Week 1)
- [ ] `validate_logsource_match()` - Matching logic
- [ ] `validate_rule()` - Rule structure validation
- [ ] `validate_rule_view()` - Rule view validation

### Phase 1c: Filters (Week 2)
- [ ] `filter_rules_by_logsource()` - Main filter
- [ ] `filter_rules_by_status()` - Status filter
- [ ] `find_matching_rule_view()` - View matching
- [ ] `find_matching_logsource_mapping()` - Mapping matching

### Phase 1d: Mappers (Week 2)
- [ ] `build_rule_to_ocsf_mapping()` - First mapping stage
- [ ] `build_ocsf_to_siem_mapping()` - Second mapping stage
- [ ] `build_siem_to_raw_mapping()` - Raw field mapping
- [ ] `build_full_field_chain()` - Complete chain
- [ ] `build_rule_field_mappings()` - Table building

### Phase 1e: Translators (Week 3)
- [ ] `translate_condition_to_splunk()` - Condition translation
- [ ] `generate_splunk_rule()` - Splunk output
- [ ] `generate_elk_rule()` - ELK output
- [ ] Add QRadar output (future)

### Phase 1f: Export & Orchestration (Week 3)
- [ ] `export_rules_to_json()` - JSON export
- [ ] `process_tenant_to_siem_rules()` - Main orchestrator

### Phase 1g: Testing & Refinement (Week 4)
- [ ] Unit tests for each function
- [ ] Integration tests for complete flow
- [ ] Manual testing on test tenant
- [ ] Documentation

---

## Part 5: Next Steps

1. **Manual Testing** (Ready): Test functions with sample data
2. **Endpoint Manual** (Phase 2): Test on actual SIEM deployment
3. **Automation** (Phase 3): Build CI/CD pipeline
4. **Scaling** (Phase 4): Support multiple tenants + bulk operations

