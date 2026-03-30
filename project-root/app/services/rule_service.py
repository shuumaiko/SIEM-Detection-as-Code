from domain.models.rule import Rule
from domain.models.tenant import Tenant
from domain.repositories.rule_repository import RuleRepository


class RuleService:
    """Application service for loading tenant rule collections."""

    def __init__(self, rule_repository: RuleRepository) -> None:
        """Store rule repository dependency."""
        self.rule_repository = rule_repository

    def load_rules_for_tenant(self, tenant: Tenant, include_all: bool = False) -> list[Rule]:
        """Load already-rendered rules for one tenant from artifact storage."""
        return self.rule_repository.list_for_tenant(tenant, include_all=include_all)

    def load_render_candidates(self, tenant: Tenant) -> list[Rule]:
        """Load source rules that support the tenant's current SIEM render path."""
        return self.rule_repository.list_render_candidates(tenant)

    def save_rendered_rules_for_tenant(self, tenant: Tenant, rendered_rules: list[dict]) -> None:
        """Persist rendered tenant rule documents into the artifact layer."""
        self.rule_repository.save_rendered_for_tenant(tenant, rendered_rules)

    def sync_artifact_enabled_states(self, tenant: Tenant) -> None:
        """Refresh persisted artifact enabled flags from the tenant deployment manifest."""
        self.rule_repository.sync_artifact_enabled_states(tenant)
