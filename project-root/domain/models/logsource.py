from dataclasses import dataclass


@dataclass
class LogSource:
    device_id: str
    service_id: str
    category: str
    status: str = "active"
