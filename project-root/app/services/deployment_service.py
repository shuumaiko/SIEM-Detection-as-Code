from domain.models.rule import Rule
from infrastructure.siem.base_adapter import BaseSIEMAdapter


class DeploymentService:
    """Application service that delegates rule deployment to SIEM adapter."""

    def __init__(self, siem_adapter: BaseSIEMAdapter) -> None:
        """Store SIEM adapter dependency."""
        self.siem_adapter = siem_adapter

    def deploy(self, tenant_id: str, rules: list[Rule]) -> dict:
        """Deploy provided rules to tenant SIEM."""
        return self.siem_adapter.deploy_rules(tenant_id, rules)
