from dataclasses import dataclass


@dataclass
class Rule:
    rule_id: str
    category: str
    product: str | None = None
    siem_query: str | None = None
    siem_targets: dict | None = None
    raw: dict | None = None
