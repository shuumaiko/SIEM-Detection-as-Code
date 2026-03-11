from domain.models.rule import Rule
from domain.models.tenant import Tenant
from domain.repositories.rule_repository import RuleRepository


class RuleService:
    """Application service for loading tenant rule collections."""

    def __init__(self, rule_repository: RuleRepository) -> None:
        self.rule_repository = rule_repository

    def load_rules_for_tenant(self, tenant: Tenant, include_all: bool = False) -> list[Rule]:
        return self.rule_repository.list_for_tenant(tenant, include_all=include_all)
