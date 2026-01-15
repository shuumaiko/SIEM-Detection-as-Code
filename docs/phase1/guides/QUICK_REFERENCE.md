# SIEM Detection Phase 1 - Quick Reference Card

## One-Page Overview

### The Pipeline (6 Stages)
```
Load Tenant → Load Rules → Filter → Map Fields → Generate SIEM → Export JSON
```

### 21 Functions Organized by Role

| Role | Functions | Count |
|------|-----------|-------|
| 🔧 **LOADER** | load_yaml • load_tenant_config • load_rules • load_rule_views • load_mappings | 5 |
| ✓ **VALIDATOR** | validate_logsource • validate_rule • validate_view | 3 |
| 🎯 **FILTER** | filter_by_logsource • filter_by_status • find_rule_view • find_mapping | 4 |
| 🔗 **MAPPER** | rule_to_ocsf • ocsf_to_siem • siem_to_raw • build_full_chain | 4 |
| 📝 **TRANSLATOR** | generate_splunk • generate_elk | 2 |
| 💾 **EXPORTER** | export_to_json • export_summary | 2 |
| 🎭 **ORCHESTRATOR** | process_tenant_to_siem_rules | 1 |

---

## Field Mapping Chain

```
Detection Rule Field
    ↓ (Rule View)
OCSF Normalized Field
    ↓ (Logsource Mapping)
SIEM Field Name
    ↓
Vendor Native Field
```

**Example: src_ip**
```
src_ip (rule)
  → ocsf.source.ip (standard)
  → src (Splunk/checkpoint)
  → src (native checkpoint field)
```

---

## Data Files Structure

```
1. Tenant Config (4 files)
   ├── tenant.yaml (metadata)
   ├── device.yml (devices)
   ├── logsource.yaml (data sources)
   └── ruleset.yaml (optional: enabled rules)

2. Detection Rules
   └── rules/detection/**/rule-*.yml

3. Rule Views (field → ocsf mappings)
   └── rule-views/**/rule-view-*.yml

4. Logsource Mappings (ocsf → siem mappings)
   └── logsource-mapping-registry/vendor/*/mapping.yml
```

---

## Processing Sequence

```
Step 1: Load
  ├─ DataLoader.load_tenant_config()
  ├─ DataLoader.load_rules()
  ├─ DataLoader.load_rule_views()
  └─ DataLoader.load_logsource_mappings()

Step 2: Validate & Filter
  ├─ DataValidator.validate_logsource_match()
  └─ DataFilter.filter_rules_by_logsource()

Step 3: Match & Map
  ├─ DataFilter.find_matching_rule_view()
  ├─ DataFilter.find_matching_mapping()
  └─ FieldMapper.build_ocsf_to_siem_mapping()

Step 4: Translate
  ├─ SIEMTranslator.generate_splunk_rule()
  └─ SIEMTranslator.generate_elk_rule()

Step 5: Export
  └─ DataExporter.export_to_json()
```

---

## Quick Start Code

```python
from tools.phase1_processor import ProcessOrchestrator

# Run complete pipeline
results = ProcessOrchestrator.process_tenant_to_siem_rules(
    tenant_path="./tenant-manager/tenants/tenant-A",
    rules_dir="./rules/detection",
    rule_views_dir="./rule-views",
    mappings_dir="./logsource-mapping-registry",
    output_file="./siem-rule.json",
    siem_type="splunk"  # or "elk"
)

# Check results
print(f"Generated: {results['statistics']['siem_rules_generated']} rules")
print(f"Mappings: {results['statistics']['field_mappings_created']}")
```

---

## Key Files to Remember

| File | Purpose | Size |
|------|---------|------|
| ARCHITECTURE_ANALYSIS.md | Full design | 15 KB |
| IMPLEMENTATION_GUIDE.md | Specifications | 25 KB |
| tools/phase1_processor.py | Code | 12 KB |
| PHASE1_DEMO.ipynb | Interactive demo | 8 KB |
| PHASE1_SUMMARY.md | This summary | 10 KB |

---

## Common Tasks

### Load tenant config
```python
from tools.phase1_processor import DataLoader
config = DataLoader.load_tenant_config("./tenant-manager/tenants/tenant-A")
```

### Filter compatible rules
```python
compatible = DataFilter.filter_rules_by_logsource(all_rules, config['logsources'])
```

### Build field mapping for a single rule
```python
view = DataFilter.find_matching_rule_view(rule['logsource'], rule_views)
mapping = DataFilter.find_matching_mapping(vendor, product, service, mappings)
chain = FieldMapper.build_full_chain('src_ip', view, ocsf_to_siem)
```

### Generate Splunk rule
```python
splunk_rule = SIEMTranslator.generate_splunk_rule(rule, mappings, tenant, device)
```

### Export to JSON
```python
DataExporter.export_to_json(rules, mappings, tenant, 'output.json')
```

---

## Logsource Matching Logic

```
RULE Logsource:
  category: firewall
  product: any            ← 'any' is wildcard!
  service: traffic

CONFIG Logsource:
  vendor: checkpoint
  product: checkpoint
  service: traffic
  enabled: true

MATCH? YES
  Because rule's product is 'any' (accepts any product)
  AND categories match (firewall == firewall)
  AND services match (traffic == traffic)
  AND config is enabled
```

---

## Error Handling

| Phase | Errors | Recovery |
|-------|--------|----------|
| Load | File not found, YAML syntax | Exit with error (required) |
| Validate | Schema mismatch | Warn + skip rule |
| Filter | No matching mappings | Warn + skip (continue) |
| Map | Field not found | Skip field + continue |
| Generate | Syntax error | Use raw condition + warn |
| Export | Write error | Retry or use alt path |

---

## Next Steps After Phase 1

1. **Phase 1b**: Integrate into main.py (add error logging, testing)
2. **Phase 1c**: Manual test on Splunk (deploy tenant-A rules)
3. **Phase 1d**: Verify field mappings in SIEM
4. **Phase 2**: Add multi-tenant support
5. **Phase 3**: Automate deployment pipeline
6. **Phase 4**: Add monitoring & alerting

---

## Statistics from Demo

```
Total Rules Loaded: 20
Compatible Rules: 8 (40%)
Active Rules: 8 (100% of compatible)
SIEM Rules Generated: 16 (8 rules × 2 devices)
Field Mappings Created: 16
Output File: siem-rule.json
```

---

## Function Call Graph

```
process_tenant_to_siem_rules() [ORCHESTRATOR]
├─ load_tenant_config() [LOADER]
├─ load_rules_from_dir() [LOADER]
├─ load_rule_views() [LOADER]
├─ load_logsource_mappings() [LOADER]
├─ filter_rules_by_logsource() [FILTER]
│  └─ validate_logsource_match() [VALIDATOR]
├─ filter_by_status() [FILTER]
└─ For each rule & device:
   ├─ find_matching_rule_view() [FILTER]
   ├─ find_matching_mapping() [FILTER]
   ├─ build_ocsf_to_siem_mapping() [MAPPER]
   ├─ generate_splunk_rule() [TRANSLATOR]
   └─ export_to_json() [EXPORTER]
```

---

## Configuration Example

**tenant-A/tenant.yaml**
```yaml
tenant_id: tenant-a
name: Company A
environment: production
siem_target: splunk
```

**tenant-A/device.yml**
```yaml
- device_id: fg-hq-01
  vendor: checkpoint
  product: checkpoint
  role: firewall
```

**tenant-A/logsource.yaml**
```yaml
- vendor: checkpoint
  product: checkpoint
  service: traffic
  enabled: true
```

---

## Design Principles

✓ **Single Responsibility**: Each function does ONE thing  
✓ **DRY (Don't Repeat Yourself)**: Reusable functions  
✓ **Fail Fast**: Validate early  
✓ **Clear Names**: Function names describe purpose  
✓ **Error Handling**: Try/catch with recovery  
✓ **Composable**: Functions combine easily  
✓ **Testable**: Each function is independently testable  

---

**Created**: January 15, 2026  
**Version**: 1.0  
**Status**: Ready for Implementation  
**Files**: 5 documents + code  
**Total Size**: ~80 KB  
