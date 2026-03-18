from domain.models.tenant import Tenant
from domain.repositories.tenant_repository import TenantRepository


class TenantService:
    """Application service for tenant-related operations."""

    def __init__(self, tenant_repository: TenantRepository) -> None:
        """Store tenant repository dependency."""
        self.tenant_repository = tenant_repository

    def load_tenant(self, tenant_id: str) -> Tenant:
        """Load one tenant from repository by tenant id."""
        return self.tenant_repository.get_by_id(tenant_id)
