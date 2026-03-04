from app.services.rule_format_validator import RuleFormatValidator


class ValidateRuleFormatUseCase:
    """Use case for validating deployed detection rule format."""

    def __init__(self, validator: RuleFormatValidator) -> None:
        self.validator = validator

    def execute(self, since: str | None = None, validate_all: bool = False) -> dict:
        """Validate detection rules using --all or --since dd/mm/yyyy."""
        return self.validator.validate(since=since, validate_all=validate_all)
