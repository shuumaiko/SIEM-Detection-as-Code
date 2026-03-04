from app.services.export_service import ExportService
from app.services.rule_service import RuleService
from domain.repositories.rule_repository import RuleRepository
from domain.repositories.tenant_repository import TenantRepository


class ExportRulesUseCase:
    """Use case for reading tenant rules and exporting normalized payload."""

    def __init__(self, tenant_repository: TenantRepository, rule_repository: RuleRepository) -> None:
        """Create use case with tenant/rule repositories."""
        self.tenant_repository = tenant_repository
        self.rule_service = RuleService(rule_repository)
        self.export_service = ExportService()

    def execute(self, tenant_id: str) -> list[dict]:
        """Execute export flow for a tenant."""
        _ = self.tenant_repository.get_by_id(tenant_id)
        rules = self.rule_service.load_rules_for_tenant(tenant_id)
        return self.export_service.export_rules(rules)
