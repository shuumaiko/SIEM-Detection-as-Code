from abc import ABC, abstractmethod

from domain.models.rule import Rule


class BaseSIEMAdapter(ABC):
    """Abstract SIEM adapter interface."""

    @abstractmethod
    def deploy_rules(self, tenant_id: str, rules: list[Rule]) -> dict:
        """Deploy rule list for one tenant and return deployment summary."""
        raise NotImplementedError
