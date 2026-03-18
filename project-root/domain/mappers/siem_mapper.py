from domain.models.rule import Rule


class SIEMMapper:
    """Map canonical rule model into SIEM-specific payloads."""

    def to_siem_payload(self, rule: Rule, siem_id: str) -> dict:
        """Build SIEM payload dictionary for one rule."""
        # Placeholder: convert canonical rule into SIEM-specific payload.
        return {
            "siem_id": siem_id,
            "rule_id": rule.rule_id,
            "payload": rule.raw or {},
        }
