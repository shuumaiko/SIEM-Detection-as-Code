from abc import ABC, abstractmethod

from domain.models.tenant import Tenant


class TenantRepository(ABC):
    """Port for tenant persistence/read access."""

    @abstractmethod
    def get_by_id(self, tenant_id: str) -> Tenant:
        """Return tenant model by id."""
        raise NotImplementedError

    @abstractmethod
    def save_rule_deployments(self, tenant_id: str, payload: dict) -> None:
        """Persist rule-deployments.yaml for one tenant."""
        raise NotImplementedError
