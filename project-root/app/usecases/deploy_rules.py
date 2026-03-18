from app.services.deployment_service import DeploymentService
from domain.models.rule import Rule
from domain.repositories.rule_repository import RuleRepository
from domain.repositories.tenant_repository import TenantRepository
from infrastructure.siem.base_adapter import BaseSIEMAdapter


class DeployRulesUseCase:
    """Deploy exported prebuilt rules to tenant SIEM."""

    def __init__(
        self,
        tenant_repository: TenantRepository,
        rule_repository: RuleRepository,
        siem_adapter: BaseSIEMAdapter,
    ) -> None:
        self.tenant_repository = tenant_repository
        self.rule_repository = rule_repository
        self.deployment_service = DeploymentService(siem_adapter)

    def execute(self, tenant_id: str, exported_rules: list[dict] | None = None) -> dict:
        if exported_rules:
            rules = [self._from_export_item(item) for item in exported_rules]
        else:
            tenant = self.tenant_repository.get_by_id(tenant_id)
            rules = self.rule_repository.list_for_tenant(tenant)
        return self.deployment_service.deploy(tenant_id, rules)

    def _from_export_item(self, item: dict) -> Rule:
        return Rule(
            rule_id=item["id"],
            category=item.get("category", "unknown"),
            product=item.get("product"),
            siem_query=item.get("search_query"),
            siem_targets=item.get("targets"),
            raw=item,
        )
