from dataclasses import dataclass


@dataclass
class RuleView:
    category: str
    device: str
    fields_map: dict
