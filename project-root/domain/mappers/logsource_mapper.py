from domain.models.rule import Rule


class LogSourceMapper:
    """Map canonical rules with tenant logsource bindings."""

    def apply_logsource(self, rule: Rule, binding: dict | None = None) -> Rule:
        """Inject binding metadata into rule payload."""
        # Placeholder: inject SIEM index/sourcetype from tenant logsource bindings.
        if binding:
            rule.raw = {**(rule.raw or {}), "_binding": binding}
        return rule
