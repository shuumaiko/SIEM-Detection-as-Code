from domain.models.rule import Rule


class RuleMapper:
    """Map raw rule content into canonical rule representation."""

    def to_standard_fields(self, rule: Rule, rule_view: dict | None = None) -> Rule:
        """Apply rule-view hints to standardize rule fields."""
        # Placeholder: apply rule-view mapping to standardize rule fields.
        if rule_view:
            rule.raw = {**(rule.raw or {}), "_rule_view": rule_view}
        return rule
