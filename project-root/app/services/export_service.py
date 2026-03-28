from domain.models.rule import Rule
from domain.models.tenant import Tenant


class ExportService:
    """Serialize source rules into the flat payload used by the render pipeline."""

    def export_rules(self, tenant: Tenant, rules: list[Rule]) -> list[dict]:
        """Return rule payloads that are ready for target resolution and rendering."""
        return [
            {
                "tenant_id": tenant.tenant_id,
                "siem_id": tenant.siem_id,
                "id": rule.rule_id,
                "display_name": (rule.raw or {}).get("title", rule.rule_id),
                "category": rule.category,
                "product": rule.product,
                "service": ((rule.raw or {}).get("logsource") or {}).get("service"),
                "search_query": rule.siem_query,
                "targets": rule.siem_targets or {},
            }
            for rule in rules
        ]
