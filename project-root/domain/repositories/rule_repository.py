from abc import ABC, abstractmethod

from domain.models.rule import Rule
from domain.models.tenant import Tenant


class RuleRepository(ABC):
    """Port for rule persistence/read access."""

    @abstractmethod
    def list_by_category(self, category: str) -> list[Rule]:
        """Return base rules filtered by category."""
        raise NotImplementedError

    @abstractmethod
    def list_for_tenant(self, tenant: Tenant, include_all: bool = False) -> list[Rule]:
        """Return effective rules for one tenant."""
        raise NotImplementedError
