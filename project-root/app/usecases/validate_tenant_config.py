from app.services.tenant_config_validator import TenantConfigValidator


class ValidateTenantConfigUseCase:
    """Use case for validating one tenant configuration set."""

    def __init__(self, validator: TenantConfigValidator) -> None:
        self.validator = validator

    def execute(self, tenant_id: str) -> dict:
        """Validate tenant configuration files and references."""
        return self.validator.validate(tenant_id)
