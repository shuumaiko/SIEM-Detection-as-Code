from domain.models.rule import Rule
from domain.repositories.rule_repository import RuleRepository


class RuleService:
    """Application service for loading rule collections."""

    def __init__(self, rule_repository: RuleRepository) -> None:
        """Store rule repository dependency."""
        self.rule_repository = rule_repository

    def load_rules_for_tenant(self, tenant_id: str) -> list[Rule]:
        """Resolve rule list for a tenant."""
        return self.rule_repository.list_for_tenant(tenant_id)
