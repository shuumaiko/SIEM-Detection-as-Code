from domain.models.rule import Rule


class ExportService:
    """Application service to shape exported rule payloads."""

    def export_rules(self, rules: list[Rule]) -> list[dict]:
        """Serialize domain Rule objects into lightweight dictionaries."""
        # Placeholder: serialize exported rules to file/API payload.
        return [
            {"id": r.rule_id, "category": r.category, "product": r.product}
            for r in rules
        ]
