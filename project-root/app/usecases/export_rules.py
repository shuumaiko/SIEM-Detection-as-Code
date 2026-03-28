from app.services.export_service import ExportService
from app.services.rule_artifact_service import RuleArtifactService
from app.services.rule_deployment_builder import RuleDeploymentBuilder
from app.services.rule_service import RuleService
from domain.repositories.rule_repository import RuleRepository
from domain.repositories.tenant_repository import TenantRepository


class ExportRulesUseCase:
    """Render source rules into tenant artifacts and refresh rule-deployments.yaml."""

    def __init__(
        self,
        tenant_repository: TenantRepository,
        rule_repository: RuleRepository,
        deployment_builder: RuleDeploymentBuilder,
        artifact_service: RuleArtifactService,
    ) -> None:
        """Store dependencies used by the hardcoded-query render pipeline."""
        self.tenant_repository = tenant_repository
        self.rule_service = RuleService(rule_repository)
        self.export_service = ExportService()
        self.deployment_builder = deployment_builder
        self.artifact_service = artifact_service

    def execute(self, tenant_id: str) -> list[dict]:
        """Render source rules into artifacts and return the flattened rendered payload."""
        tenant = self.tenant_repository.get_by_id(tenant_id)
        rules = self.rule_service.load_render_candidates(tenant)
        exported = self.export_service.export_rules(tenant, rules)
        mapped_rules, deployment_payload = self.deployment_builder.build(tenant, exported)
        artifact_rules = self.artifact_service.build_artifacts(tenant, rules, mapped_rules)
        self.rule_service.save_rendered_rules_for_tenant(tenant.tenant_id, artifact_rules)
        self.tenant_repository.save_rule_deployments(tenant_id, deployment_payload)
        return mapped_rules
