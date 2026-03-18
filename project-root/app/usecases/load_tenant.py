from app.services.tenant_service import TenantService
from domain.models.tenant import Tenant
from domain.repositories.tenant_repository import TenantRepository


class LoadTenantUseCase:
    """Use case for loading one tenant from configured storage."""

    def __init__(self, tenant_repository: TenantRepository) -> None:
        """Create use case with tenant repository port."""
        self.tenant_service = TenantService(tenant_repository)

    def execute(self, tenant_id: str) -> Tenant:
        """Execute load tenant flow."""
        return self.tenant_service.load_tenant(tenant_id)
