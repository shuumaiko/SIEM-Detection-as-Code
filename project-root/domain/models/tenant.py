from dataclasses import dataclass, field

from domain.models.binding import Binding
from domain.models.device import Device
from domain.models.logsource import LogSource
from domain.models.rule_deployment import RuleDeployment


@dataclass
class Tenant:
    tenant_id: str
    siem_id: str | None = None
    devices: dict[str, Device] = field(default_factory=dict)
    logsources: dict[str, LogSource] = field(default_factory=dict)
    bindings: dict[str, Binding] = field(default_factory=dict)
    rule_deployments: list[RuleDeployment] = field(default_factory=list)

    def enabled_rule_ids(self) -> set[str]:
        return {item.rule_id for item in self.rule_deployments if item.enabled}
