# import customer-env-config.yml as custom_env
import yaml

# xác định input và output cho hàm
# Input: config_file - file YAML chứa logsource, siem_type, vendor, product
# Output: tệp rules tương ứng
def generate_rules(config_file):
    """
    Sinh ra rules dựa trên cấu hình từ file YAML
    
    Args:
        config_file (str): Đường dẫn đến file config.yml chứa:
            - logsource: Loại log source
            - siem_type: Loại SIEM (Splunk, ELK, QRadar)
            - vendor: Nhà cung cấp sản phẩm (tuỳ chọn)
            - product: Tên sản phẩm (tuỳ chọn)
    
    Returns:
        list: Danh sách các rules được sinh ra
    """
    # Load cấu hình từ file YAML
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Không tìm thấy file config: {config_file}")
    except yaml.YAMLError as e:
        raise ValueError(f"Lỗi khi đọc file YAML: {e}")
    
    # Trích xuất các thông tin từ config
    logsource = config.get('logsource')
    siem_type = config.get('siem_type')
    vendor = config.get('vendor')
    product = config.get('product')
    
    # Kiểm tra các thông tin bắt buộc
    if not logsource:
        raise ValueError("logsource là bắt buộc trong file config")
    if not siem_type:
        raise ValueError("siem_type là bắt buộc trong file config")
    
    rules = []
    # xác định đường dẫn của tệp rules dựa trên loại siem
    if siem_type == "Splunk":
        rules_file_path = f"rules/splunk/{logsource}.spl"
    elif siem_type == "ELK":
        rules_file_path = f"rules/elk/{logsource}.json"
    elif siem_type == "QRadar":
        rules_file_path = f"rules/qradar/{logsource}.sql"
    else:
        raise ValueError("Unsupported SIEM type")

    # Kiểm tra loại SIEM và tạo quy tắc tương ứng
    if siem_type == "Splunk":
        rule = f"source={logsource} | stats count by {vendor} {product}"
        rules.append(rule)
    elif siem_type == "ELK":
        rule = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"logsource": logsource}},
                        {"match": {"vendor": vendor}} if vendor else {},
                        {"match": {"product": product}} if product else {}
                    ]
                }
            }
        }
        rules.append(rule)
    elif siem_type == "QRadar":
        rule = f"SELECT * FROM events WHERE logsource='{logsource}'"
        if vendor:
            rule += f" AND vendor='{vendor}'"
        if product:
            rule += f" AND product='{product}'"
        rules.append(rule)
    else:
        raise ValueError("Unsupported SIEM type")
    
    return rules