from dataclasses import dataclass


@dataclass
class TenantSource:
    category: str
    service_id: str
    device_type: str
    device_id: str
    status: str
    siem_id: str
    index: str
    sourcetype: str
