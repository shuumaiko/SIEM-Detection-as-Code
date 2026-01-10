import sys
import os
from function import *

def main():
    """
    Hàm chính để sinh ra rules từ file customer-env-config.yml
    """
    # Kiểm tra xem có tham số customer được truyền hay không
    if len(sys.argv) < 2:
        customer_name = "customer-A"  # Mặc định dùng customer-A
        print(f"Cảnh báo: Không tìm thấy tham số customer. Dùng mặc định: {customer_name}")
    else:
        customer_name = sys.argv[1]
        print(f"Sử dụng customer: {customer_name}")
    
    # Xây dựng đường dẫn config file dựa trên tên customer
    config_file = f"./customer/{customer_name}/{customer_name}-env-config.yml"
    print(f"Dùng config file: {config_file}")
    
    # Kiểm tra xem file config có tồn tại hay không
    if not os.path.exists(config_file):
        print(f"Lỗi: File config '{config_file}' không tồn tại.")
        print(f"Thư mục hiện tại: {os.getcwd()}")
        print(f"Files trong thư mục hiện tại: {os.listdir('.')}")
        sys.exit(1)
    
    # try:
    #     # Gọi hàm generate_rules để sinh ra rules
    #     rules = generate_rules(config_file)
        
    #     # In ra các rules được sinh ra
    #     print(f"Đã sinh ra {len(rules)} rule(s):")
    #     print("-" * 50)
    #     for i, rule in enumerate(rules, 1):
    #         print(f"Rule {i}:")
    #         if isinstance(rule, dict):
    #             import json
    #             print(json.dumps(rule, indent=2, ensure_ascii=False))
    #         else:
    #             print(rule)
    #         print()
        
    #     print("-" * 50)
    #     print("Hoàn thành!")
        
    # except FileNotFoundError as e:
    #     print(f"Lỗi: {e}")
    #     sys.exit(1)
    # except ValueError as e:
    #     print(f"Lỗi: {e}")
    #     sys.exit(1)
    # except Exception as e:
    #     print(f"Lỗi không mong muốn: {e}")
    #     sys.exit(1)

if __name__ == "__main__":
    main()
