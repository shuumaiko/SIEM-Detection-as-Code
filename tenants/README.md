tenant-manager/
├── README.md
│
├── tenants/
│   ├── tenant-a/
│   │   ├── tenant.yaml            # Thông tin tenant
│   │   ├── devices.yaml           # Danh sách thiết bị
│   │   ├── logsources.yaml        # Logsource enable
│   │   ├── capabilities.yaml      # Khả năng (feature, log coverage)
│   │   ├── versions.yaml          # Version firmware / OS
│   │   └── ruleset.yaml            # Rule enable / disable
│   │
│   └── tenant-b/
│       └── ...
│
├── schemas/
│   ├── tenant.schema.yaml
│   ├── device.schema.yaml
│   ├── logsource.schema.yaml
│   └── ruleset.schema.yaml
│
└── globals/
    ├── default-capabilities.yaml
    └── supported-platforms.yaml

<!-- Tách ruleset.yaml khỏi rules-tenants/? -->

tenant-manager = quyết định
rules-tenants = kết quả render

# Control flow
tenant-manager
   ↓
tools
   ↓
rules-tenants (generated) <!-- future -->

Base rule
  ↓
Rule-view
  ↓
Tenant ruleset
  ↓
Capability + version check
  ↓
Rendered rule
