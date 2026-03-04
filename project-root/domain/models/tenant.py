from dataclasses import dataclass


@dataclass
class Tenant:
    tenant_id: str
    siem_id: str | None = None
