from app.services.deployment_service import DeploymentService
from domain.models.rule import Rule
from domain.repositories.rule_repository import RuleRepository
from infrastructure.siem.base_adapter import BaseSIEMAdapter


class DeployRulesUseCase:
    """Use case for deploying rules to a target SIEM."""

    def __init__(self, rule_repository: RuleRepository, siem_adapter: BaseSIEMAdapter) -> None:
        """Create use case with rule repository and SIEM adapter."""
        self.rule_repository = rule_repository
        self.deployment_service = DeploymentService(siem_adapter)

    def execute(self, tenant_id: str, exported_rules: list[dict] | None = None) -> dict:
        """Execute deploy flow, optionally using pre-exported rule payloads."""
        rules = self.rule_repository.list_for_tenant(tenant_id)
        if exported_rules:
            rules = [
                Rule(rule_id=item["id"], category=item["category"], product=item.get("product"))
                for item in exported_rules
            ]
        return self.deployment_service.deploy(tenant_id, rules)
