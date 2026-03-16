from dataclasses import dataclass, field


@dataclass
class Binding:
    tenant_id: str
    device_id: str
    siem_id: str
    bindings: dict[str, dict] = field(default_factory=dict)
    field_mappings: dict[str, dict] = field(default_factory=dict)
