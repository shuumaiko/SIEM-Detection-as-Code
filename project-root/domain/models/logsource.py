from dataclasses import dataclass, field


@dataclass
class LogSource:
    device_id: str
    status: str = "active"
    datasets: list[dict] = field(default_factory=list)
