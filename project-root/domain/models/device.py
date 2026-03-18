from dataclasses import dataclass


@dataclass
class Device:
    tenant_id: str
    device_id: str
    device_type: str | None = None
    vendor: str | None = None
    product: str | None = None
