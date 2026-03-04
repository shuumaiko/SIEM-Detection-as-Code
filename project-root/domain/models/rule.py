from dataclasses import dataclass


@dataclass
class Rule:
    rule_id: str
    category: str
    product: str | None = None
    raw: dict | None = None
