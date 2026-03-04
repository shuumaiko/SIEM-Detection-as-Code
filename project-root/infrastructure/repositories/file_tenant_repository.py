from pathlib import Path

from domain.models.tenant import Tenant
from domain.repositories.tenant_repository import TenantRepository
from infrastructure.file_loader.yaml_loader import YamlLoader


class FileTenantRepository(TenantRepository):
    """File-backed tenant repository implementation."""

    def __init__(self, base_path: str) -> None:
        """Create repository with tenant root directory."""
        self.base_path = Path(base_path)
        self.loader = YamlLoader()

    def get_by_id(self, tenant_id: str) -> Tenant:
        """Load tenant from `<base_path>/<tenant_id>/tenant.yaml`."""
        tenant_file = self.base_path / tenant_id / "tenant.yaml"
        if not tenant_file.exists():
            return Tenant(tenant_id=tenant_id)

        data = self.loader.load(tenant_file)
        return Tenant(
            tenant_id=data.get("tenant_id", tenant_id),
            siem_id=data.get("siem_id"),
        )
