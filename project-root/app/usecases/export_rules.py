from app.services.export_service import ExportService
from app.services.rule_deployment_builder import RuleDeploymentBuilder
from app.services.rule_service import RuleService
from domain.repositories.rule_repository import RuleRepository
from domain.repositories.tenant_repository import TenantRepository


class ExportRulesUseCase:
    """Read tenant-rules, map with registry and persist rule-deployments.yaml."""

    def __init__(
        self,
        tenant_repository: TenantRepository,
        rule_repository: RuleRepository,
        deployment_builder: RuleDeploymentBuilder,
    ) -> None:
        self.tenant_repository = tenant_repository
        self.rule_service = RuleService(rule_repository)
        self.export_service = ExportService()
        self.deployment_builder = deployment_builder

    def execute(self, tenant_id: str) -> list[dict]:
        tenant = self.tenant_repository.get_by_id(tenant_id)
        rules = self.rule_service.load_rules_for_tenant(tenant, include_all=True)
        exported = self.export_service.export_rules(tenant, rules)
        mapped_rules, deployment_payload = self.deployment_builder.build(tenant, exported)
        self.tenant_repository.save_rule_deployments(tenant_id, deployment_payload)
        return mapped_rules
