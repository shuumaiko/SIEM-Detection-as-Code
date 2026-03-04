from abc import ABC, abstractmethod

from domain.models.rule import Rule


class RuleRepository(ABC):
    """Port for rule persistence/read access."""

    @abstractmethod
    def list_by_category(self, category: str) -> list[Rule]:
        """Return rules filtered by category."""
        raise NotImplementedError

    @abstractmethod
    def list_for_tenant(self, tenant_id: str) -> list[Rule]:
        """Return rules applicable for a tenant."""
        raise NotImplementedError
