"""
SIEM Detection - Phase 1 Implementation
Demo Functions for Tenant Config → SIEM Rule Export

Functions organized by role:
1. Loaders (Data Loading)
2. Validators (Data Validation)
3. Filters (Selection & Filtering)
4. Mappers (Field Mapping)
5. Translators (Syntax Generation)
6. Exporters (Output Generation)
7. Orchestrators (Process Control)
"""

import os
import json
import yaml
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path


# ============================================================================
# ROLE 1: DATA LOADERS
# ============================================================================

def load_yaml_file(file_path: str) -> Dict[str, Any]:
    """
    Load YAML file and return as dictionary.
    
    Args:
        file_path: Path to YAML file
        
    Returns:
        Dict containing parsed YAML content
        
    Raises:
        FileNotFoundError: If file doesn't exist
        yaml.YAMLError: If file has invalid YAML syntax
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = yaml.safe_load(f)
            return content if content is not None else {}
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Invalid YAML in {file_path}: {e}")


def load_tenant_config(tenant_base_path: str) -> Dict[str, Any]:
    """
    Load complete tenant configuration (tenant, device, logsource, ruleset).
    
    Args:
        tenant_base_path: Path to tenant directory (e.g., './tenant-manager/tenants/tenant-A')
        
    Returns:
        Dict with keys: tenant, devices, logsources, ruleset
    """
    config = {}
    
    # Load tenant metadata
    tenant_file = os.path.join(tenant_base_path, 'tenant.yaml')
    config['tenant'] = load_yaml_file(tenant_file)
    
    # Load device list
    device_file = os.path.join(tenant_base_path, 'device.yml')
    devices = load_yaml_file(device_file)
    config['devices'] = devices if isinstance(devices, list) else [devices]
    
    # Load logsource configuration
    logsource_file = os.path.join(tenant_base_path, 'logsource.yaml')
    logsources = load_yaml_file(logsource_file)
    config['logsources'] = logsources if isinstance(logsources, list) else [logsources]
    
    # Load ruleset (optional)
    ruleset_file = os.path.join(tenant_base_path, 'ruleset.yaml')
    if os.path.exists(ruleset_file):
        ruleset = load_yaml_file(ruleset_file)
        config['ruleset'] = ruleset if isinstance(ruleset, list) else []
    else:
        config['ruleset'] = []
    
    return config


def load_rules(rules_dir: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Load all detection rules from rules directory.
    
    Args:
        rules_dir: Path to rules directory
        category: Optional filter by category (e.g., 'network', 'endpoint')
        
    Returns:
        List of rule dictionaries
    """
    rules = []
    
    # Find all rule files matching pattern rule-*.yml or rule-*.yaml
    for root, dirs, files in os.walk(rules_dir):
        for file in files:
            if file.startswith('net_fw_') and file.endswith('.yml'):
                file_path = os.path.join(root, file)
                try:
                    rule = load_yaml_file(file_path)
                    # Handle multiple rules in one file (separated by ---)
                    if isinstance(rule, str):
                        # Manually parse multi-document YAML
                        with open(file_path, 'r', encoding='utf-8') as f:
                            for doc in yaml.safe_load_all(f):
                                if doc:
                                    rules.append(doc)
                    else:
                        rules.append(rule)
                except Exception as e:
                    print(f"Warning: Failed to load rule {file_path}: {e}")
    
    return rules


def load_rule_views(rule_views_dir: str) -> List[Dict[str, Any]]:
    """
    Load all rule view definitions.
    
    Args:
        rule_views_dir: Path to rule-views directory
        
    Returns:
        List of rule view dictionaries
    """
    rule_views = []
    
    for root, dirs, files in os.walk(rule_views_dir):
        for file in files:
            if file.startswith('rule-view-') and file.endswith('.yml'):
                file_path = os.path.join(root, file)
                try:
                    rule_view = load_yaml_file(file_path)
                    rule_views.append(rule_view)
                except Exception as e:
                    print(f"Warning: Failed to load rule view {file_path}: {e}")
    
    return rule_views


def load_logsource_mappings(mappings_dir: str) -> List[Dict[str, Any]]:
    """
    Load all logsource mapping definitions.
    
    Args:
        mappings_dir: Path to logsource-mapping-registry directory
        
    Returns:
        List of mapping dictionaries
    """
    mappings = []
    
    for root, dirs, files in os.walk(mappings_dir):
        for file in files:
            if file.endswith('-mapping.yml') or file.endswith('-convert-field.yml'):
                file_path = os.path.join(root, file)
                try:
                    mapping = load_yaml_file(file_path)
                    mappings.append(mapping)
                except Exception as e:
                    print(f"Warning: Failed to load mapping {file_path}: {e}")
    
    return mappings


# ============================================================================
# ROLE 2: DATA VALIDATORS
# ============================================================================

def validate_logsource_match(rule_logsource: Dict[str, str], 
                            config_logsource: Dict[str, str]) -> bool:
    """
    Check if rule logsource matches config logsource.
    Rule logsource uses 'any' as wildcard.
    
    Args:
        rule_logsource: Logsource from rule (has category, product, service)
        config_logsource: Logsource from tenant config (has vendor, product, service)
        
    Returns:
        True if logsources match
    """
    # Rule logsource uses 'any' for product wildcard
    if rule_logsource.get('product') != 'any' and rule_logsource.get('product') != config_logsource.get('product'):
        return False
    
    if rule_logsource.get('category') != config_logsource.get('category', ''):
        return False
    
    if rule_logsource.get('service') != config_logsource.get('service'):
        return False
    
    return True


def validate_rule(rule: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate rule structure.
    
    Args:
        rule: Rule dictionary to validate
        
    Returns:
        Tuple of (is_valid: bool, errors: List[str])
    """
    errors = []
    
    # Check required fields
    required_fields = ['title', 'name', 'id', 'logsource', 'detection']
    for field in required_fields:
        if field not in rule:
            errors.append(f"Missing required field: {field}")
    
    # Validate logsource structure
    if 'logsource' in rule:
        logsource = rule['logsource']
        if 'category' not in logsource:
            errors.append("logsource missing 'category' field")
    
    # Validate detection structure
    if 'detection' in rule:
        detection = rule['detection']
        if 'condition' not in detection:
            errors.append("detection missing 'condition' field")
    
    return len(errors) == 0, errors


def validate_rule_view(rule_view: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate rule view structure.
    
    Args:
        rule_view: Rule view dictionary to validate
        
    Returns:
        Tuple of (is_valid: bool, errors: List[str])
    """
    errors = []
    
    if 'logsource' not in rule_view:
        errors.append("Missing 'logsource' field")
    
    if 'mapping' not in rule_view:
        errors.append("Missing 'mapping' field")
    
    return len(errors) == 0, errors


# ============================================================================
# ROLE 3: FILTERS & SELECTORS
# ============================================================================

def filter_rules_by_logsource(rules: List[Dict[str, Any]], 
                              logsources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter rules to only those compatible with tenant's logsources.
    
    Args:
        rules: List of all detection rules
        logsources: List of enabled logsources from tenant config
        
    Returns:
        Filtered list of compatible rules
    """
    filtered_rules = []
    
    for rule in rules:
        if 'logsource' not in rule:
            continue
        
        rule_logsource = rule['logsource']
        
        # Check if rule matches any of the tenant's logsources
        for config_logsource in logsources:
            if config_logsource.get('enabled', True):  # Skip disabled logsources
                if validate_logsource_match(rule_logsource, config_logsource):
                    filtered_rules.append(rule)
                    break
    
    return filtered_rules


def filter_rules_by_status(rules: List[Dict[str, Any]], 
                           statuses: List[str] = None) -> List[Dict[str, Any]]:
    """
    Filter rules by status (test, production, deprecated).
    
    Args:
        rules: List of rules to filter
        statuses: List of statuses to include (default: ['test', 'production'])
        
    Returns:
        Filtered rules
    """
    if statuses is None:
        statuses = ['test', 'production']
    
    return [r for r in rules if r.get('status') in statuses]


def find_matching_rule_view(rule_logsource: Dict[str, str], 
                            rule_views: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Find rule view that matches the rule's logsource.
    
    Args:
        rule_logsource: Logsource from rule
        rule_views: List of available rule views
        
    Returns:
        Matching rule view or None
    """
    for rule_view in rule_views:
        view_logsource = rule_view.get('logsource', {})
        
        # Match logic: rule_view's logsource should cover rule's logsource
        # View uses 'any' as wildcard
        if (view_logsource.get('category') == rule_logsource.get('category') and
            (view_logsource.get('product') == 'any' or 
             view_logsource.get('product') == rule_logsource.get('product')) and
            view_logsource.get('service') == rule_logsource.get('service')):
            return rule_view
    
    return None


def find_matching_logsource_mapping(vendor: str, product: str, service: str,
                                    mappings: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Find logsource mapping for vendor/product/service combination.
    
    Args:
        vendor: Vendor name
        product: Product name
        service: Service name
        mappings: List of available mappings
        
    Returns:
        Matching mapping or None
    """
    for mapping in mappings:
        logsource = mapping.get('logsource', {})
        
        if (logsource.get('vendor') == vendor and
            logsource.get('product') == product and
            logsource.get('service') == service):
            return mapping
    
    return None


# ============================================================================
# ROLE 4: FIELD MAPPERS
# ============================================================================

def build_rule_to_ocsf_mapping(rule_view: Dict[str, Any]) -> Dict[str, str]:
    """
    Extract rule field → OCSF field mapping from rule view.
    
    Args:
        rule_view: Rule view dictionary
        
    Returns:
        Dict mapping rule field names to OCSF paths (e.g., 'src_ip' → 'ocsf.source.ip')
    """
    mapping = rule_view.get('mapping', {})
    return dict(mapping)  # Returns: {rule_field: ocsf_path, ...}


def build_ocsf_to_siem_mapping(logsource_mapping: Dict[str, Any]) -> Dict[str, str]:
    """
    Extract OCSF field → SIEM field mapping from logsource mapping.
    
    Args:
        logsource_mapping: Logsource mapping dictionary
        
    Returns:
        Dict mapping OCSF paths to SIEM field names
    """
    # The logsource mapping has siem_fields section
    # which maps siem_field → ocsf path
    # We need to reverse this to ocsf → siem_field
    
    siem_fields = logsource_mapping.get('siem_fields', {})
    
    # Reverse: {siem_field: ocsf_path} → {ocsf_path: siem_field}
    ocsf_to_siem = {v: k for k, v in siem_fields.items()}
    
    return ocsf_to_siem


def build_siem_to_raw_mapping(logsource_mapping: Dict[str, Any]) -> Dict[str, str]:
    """
    Extract SIEM field → Raw field mapping from logsource mapping.
    Useful for understanding the vendor's native field names.
    
    Args:
        logsource_mapping: Logsource mapping dictionary
        
    Returns:
        Dict mapping SIEM field names to raw vendor field names
    """
    return logsource_mapping.get('siem_fields-map-to-raw_fields', {})


def build_full_field_chain(rule_field: str,
                          rule_view: Dict[str, Any],
                          ocsf_to_siem: Dict[str, str]) -> Optional[str]:
    """
    Build complete field mapping chain: rule_field → ocsf_field → siem_field
    
    Args:
        rule_field: Field name from detection rule
        rule_view: Rule view for field mapping
        ocsf_to_siem: OCSF to SIEM field mapping
        
    Returns:
        Final SIEM field name or None if mapping not found
    """
    rule_to_ocsf = build_rule_to_ocsf_mapping(rule_view)
    
    # Step 1: rule_field → ocsf_field
    ocsf_field = rule_to_ocsf.get(rule_field)
    if not ocsf_field:
        return None
    
    # Step 2: ocsf_field → siem_field
    siem_field = ocsf_to_siem.get(ocsf_field)
    if not siem_field:
        return None
    
    return siem_field


def build_rule_field_mappings(rule: Dict[str, Any],
                             rule_view: Dict[str, Any],
                             ocsf_to_siem: Dict[str, str],
                             siem_to_raw: Dict[str, str]) -> Dict[str, Dict[str, str]]:
    """
    Build field mappings for all fields in a rule.
    
    Args:
        rule: Detection rule
        rule_view: Matching rule view
        ocsf_to_siem: OCSF to SIEM mapping
        siem_to_raw: SIEM to raw field mapping
        
    Returns:
        Dict of field mappings with full chain information
    """
    fields = rule.get('fields', [])
    mappings = {}
    
    for field in fields:
        rule_to_ocsf = build_rule_to_ocsf_mapping(rule_view)
        ocsf_field = rule_to_ocsf.get(field)
        
        if ocsf_field:
            siem_field = ocsf_to_siem.get(ocsf_field)
            raw_field = siem_to_raw.get(siem_field) if siem_field else None
            
            mappings[field] = {
                'rule_field': field,
                'ocsf_field': ocsf_field,
                'siem_field': siem_field,
                'raw_field': raw_field
            }
    
    return mappings


# ============================================================================
# ROLE 5: TRANSLATORS (Syntax Generation)
# ============================================================================

def translate_condition_to_splunk(condition: str, 
                                 field_mappings: Dict[str, str]) -> str:
    """
    Translate rule detection condition to Splunk SPL syntax.
    
    Simple example: "selection_port and selection_protocol and not filter"
    
    Args:
        condition: Condition string from rule detection
        field_mappings: Mapping of rule fields to SIEM fields
        
    Returns:
        Splunk SPL query fragment
    """
    # This is a simplified example
    # Real implementation would parse complex conditions
    
    condition = condition.replace('and', '|')
    condition = condition.replace('or', 'OR')
    condition = condition.replace('not ', 'NOT ')
    
    return condition


def generate_splunk_rule(rule: Dict[str, Any],
                        field_mappings: Dict[str, Dict[str, str]],
                        tenant: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate Splunk-specific rule format.
    
    Args:
        rule: Detection rule
        field_mappings: Field mapping information
        tenant: Tenant configuration
        
    Returns:
        Splunk rule dictionary
    """
    splunk_rule = {
        'name': rule.get('name'),
        'title': rule.get('title'),
        'description': rule.get('description'),
        'search': f"sourcetype={tenant.get('siem_target')} ",  # Base search
        'detection': {
            'condition': rule.get('detection', {}).get('condition'),
            'selections': rule.get('detection', {}).get('selection_port', {})
        },
        'output_fields': [m['siem_field'] for m in field_mappings.values() if m.get('siem_field')],
        'tags': rule.get('tags', []),
        'status': rule.get('status'),
        'tenant_id': tenant.get('tenant_id')
    }
    
    return splunk_rule


def generate_elk_rule(rule: Dict[str, Any],
                      field_mappings: Dict[str, Dict[str, str]],
                      tenant: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate ELK-specific rule format (Elasticsearch query).
    
    Args:
        rule: Detection rule
        field_mappings: Field mapping information
        tenant: Tenant configuration
        
    Returns:
        ELK rule dictionary
    """
    elk_rule = {
        'rule': {
            'id': rule.get('id'),
            'name': rule.get('title'),
            'description': rule.get('description'),
            'query': {
                'bool': {
                    'must': [
                        # Example: match on source IP
                        {'match': {f['siem_field']: '${source_ip}'}}
                        for f in field_mappings.values()
                        if f.get('siem_field')
                    ]
                }
            },
            'enabled': rule.get('status') != 'deprecated',
            'tags': rule.get('tags', [])
        }
    }
    
    return elk_rule


# ============================================================================
# ROLE 6: EXPORTERS (Output Generation)
# ============================================================================

def export_rules_to_json(rules: List[Dict[str, Any]],
                        field_mappings_list: List[Dict[str, Dict[str, str]]],
                        tenant: Dict[str, Any],
                        output_file: str) -> None:
    """
    Export generated rules to siem-rule.json format.
    
    Args:
        rules: List of generated SIEM rules
        field_mappings_list: List of field mapping information for each rule
        tenant: Tenant configuration
        output_file: Path to output JSON file
    """
    export_data = {
        'metadata': {
            'tenant_id': tenant.get('tenant_id'),
            'tenant_name': tenant.get('name'),
            'environment': tenant.get('environment'),
            'siem_target': tenant.get('siem_target'),
            'export_timestamp': str(__import__('datetime').datetime.now().isoformat()),
            'version': '1.0'
        },
        'rules': rules,
        'field_mappings': field_mappings_list,
        'total_rules': len(rules)
    }
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    print(f"Exported {len(rules)} rules to {output_file}")


# ============================================================================
# ROLE 7: ORCHESTRATORS (Process Control)
# ============================================================================

def process_tenant_to_siem_rules(tenant_path: str,
                                rules_dir: str,
                                rule_views_dir: str,
                                mappings_dir: str,
                                output_file: str,
                                siem_type: str = 'splunk') -> None:
    """
    Main orchestration function: Load tenant → Generate SIEM rules → Export JSON
    
    Complete workflow for Phase 1 implementation.
    
    Args:
        tenant_path: Path to tenant configuration directory
        rules_dir: Path to detection rules directory
        rule_views_dir: Path to rule views directory
        mappings_dir: Path to logsource mappings directory
        output_file: Path to output siem-rule.json file
        siem_type: Target SIEM type ('splunk', 'elk', 'qradar')
    """
    
    print("=" * 70)
    print("PHASE 1: TENANT CONFIG → SIEM RULE EXPORT")
    print("=" * 70)
    
    try:
        # STEP 1: Load tenant configuration
        print("\n[1/6] Loading tenant configuration...")
        tenant_config = load_tenant_config(tenant_path)
        tenant = tenant_config['tenant']
        devices = tenant_config['devices']
        logsources = tenant_config['logsources']
        
        print(f"  ✓ Tenant: {tenant.get('name')} ({tenant.get('tenant_id')})")
        print(f"  ✓ SIEM Target: {tenant.get('siem_target')}")
        print(f"  ✓ Devices: {len(devices)}")
        print(f"  ✓ Logsources: {len(logsources)}")
        
        # STEP 2: Load all rules and reference data
        print("\n[2/6] Loading detection rules and reference data...")
        all_rules = load_rules(rules_dir)
        rule_views = load_rule_views(rule_views_dir)
        logsource_mappings = load_logsource_mappings(mappings_dir)
        
        print(f"  ✓ Rules loaded: {len(all_rules)}")
        print(f"  ✓ Rule views loaded: {len(rule_views)}")
        print(f"  ✓ Logsource mappings loaded: {len(logsource_mappings)}")
        
        # STEP 3: Filter rules by logsource compatibility
        print("\n[3/6] Filtering rules by logsource compatibility...")
        compatible_rules = filter_rules_by_logsource(all_rules, logsources)
        compatible_rules = filter_rules_by_status(compatible_rules)
        
        print(f"  ✓ Compatible rules: {len(compatible_rules)}")
        
        # STEP 4: Build field mappings and generate SIEM rules
        print("\n[4/6] Building field mappings...")
        generated_rules = []
        field_mappings_list = []
        
        for rule in compatible_rules:
            rule_logsource = rule.get('logsource', {})
            
            # Find matching rule view
            rule_view = find_matching_rule_view(rule_logsource, rule_views)
            if not rule_view:
                print(f"  ⚠ No rule view found for rule: {rule.get('name')}")
                continue
            
            # Find matching logsource mapping (for each configured device)
            for device in devices:
                vendor = device.get('vendor')
                product = device.get('product')
                service = rule_logsource.get('service')
                
                mapping = find_matching_logsource_mapping(vendor, product, service, logsource_mappings)
                if not mapping:
                    print(f"  ⚠ No mapping found for {vendor}/{product}/{service}")
                    continue
                
                # Build field mappings
                ocsf_to_siem = build_ocsf_to_siem_mapping(mapping)
                siem_to_raw = build_siem_to_raw_mapping(mapping)
                field_mappings = build_rule_field_mappings(rule, rule_view, ocsf_to_siem, siem_to_raw)
                
                # Generate SIEM-specific rule
                if siem_type == 'splunk':
                    siem_rule = generate_splunk_rule(rule, field_mappings, tenant)
                elif siem_type == 'elk':
                    siem_rule = generate_elk_rule(rule, field_mappings, tenant)
                else:
                    print(f"  ⚠ Unsupported SIEM type: {siem_type}")
                    continue
                
                # Add device info
                siem_rule['device_id'] = device.get('device_id')
                siem_rule['device_role'] = device.get('role')
                
                generated_rules.append(siem_rule)
                field_mappings_list.append(field_mappings)
        
        print(f"  ✓ Generated {len(generated_rules)} SIEM rules")
        
        # STEP 5: Export to JSON
        print("\n[5/6] Exporting rules to JSON...")
        export_rules_to_json(generated_rules, field_mappings_list, tenant, output_file)
        
        # STEP 6: Summary
        print("\n[6/6] Process complete!")
        print("=" * 70)
        print(f"Summary:")
        print(f"  Total rules loaded: {len(all_rules)}")
        print(f"  Compatible rules: {len(compatible_rules)}")
        print(f"  SIEM rules generated: {len(generated_rules)}")
        print(f"  Output file: {output_file}")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


# ============================================================================
# DEMO USAGE
# ============================================================================

if __name__ == "__main__":
    # Example usage
    tenant_path = "./tenant-manager/tenants/tenant-A"
    rules_dir = "./rules/detection"
    rule_views_dir = "./rule-views"
    mappings_dir = "./logsource-mapping-registry"
    output_file = "./siem-rule.json"
    
    # Uncomment to run:
    # process_tenant_to_siem_rules(tenant_path, rules_dir, rule_views_dir, mappings_dir, output_file, 'splunk')
