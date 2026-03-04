from domain.models.rule import Rule
from infrastructure.siem.base_adapter import BaseSIEMAdapter


class ElasticAdapter(BaseSIEMAdapter):
    """Skeleton adapter for Elastic deployment integration."""

    def deploy_rules(self, tenant_id: str, rules: list[Rule]) -> dict:
        """Return dry-run deployment summary for Elastic."""
        # Placeholder: call Elastic API in real implementation.
        return {
            "tenant_id": tenant_id,
            "siem": "elastic",
            "deployed": len(rules),
            "status": "dry-run",
        }
