from domain.models.rule import Rule
from infrastructure.siem.base_adapter import BaseSIEMAdapter


class ElasticAdapter(BaseSIEMAdapter):
    """Skeleton adapter for Elastic deployment integration."""

    def deploy_rules(self, tenant_id: str, rules: list[Rule]) -> dict:
        """Return dry-run deployment summary for Elastic."""
        query_ready = len([rule for rule in rules if rule.siem_query])
        return {
            "tenant_id": tenant_id,
            "siem": "elastic",
            "deployed": len(rules),
            "query_ready": query_ready,
            "status": "dry-run",
        }
