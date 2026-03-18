from dataclasses import dataclass


@dataclass
class RuleDeployment:
    rule_id: str
    enabled: bool = True
    display_name: str | None = None
