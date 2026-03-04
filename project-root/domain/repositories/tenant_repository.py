from abc import ABC, abstractmethod

from domain.models.tenant import Tenant


class TenantRepository(ABC):
    """Port for tenant persistence/read access."""

    @abstractmethod
    def get_by_id(self, tenant_id: str) -> Tenant:
        """Return tenant model by id."""
        raise NotImplementedError
