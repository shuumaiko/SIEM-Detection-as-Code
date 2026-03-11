from types import SimpleNamespace

from app.services.rule_deployment_builder import RuleDeploymentBuilder
from domain.models.rule_deployment import RuleDeployment


class _RegistryLoaderStub:
    def resolve_siem_config(self, vendor: str | None, product: str | None, siem_id: str) -> dict:
        return {}


def test_build_keeps_existing_enabled_value_for_existing_rule() -> None:
    builder = RuleDeploymentBuilder(registry_loader=_RegistryLoaderStub())
    tenant = SimpleNamespace(
        tenant_id="fis",
        siem_id="splunk",
        rule_deployments=[
            RuleDeployment(rule_id="existing-rule", enabled=False, display_name="Existing Rule"),
        ],
        devices={},
        logsources={},
        bindings={},
    )

    _, payload = builder.build(
        tenant,
        [
            {"id": "existing-rule", "display_name": "Existing Rule"},
            {"id": "new-rule", "display_name": "New Rule"},
        ],
    )

    deployments = payload["rule_deployments_by_siem"]["splunk"]

    assert deployments == [
        {"rule_id": "existing-rule", "enabled": False, "display_name": "Existing Rule"},
        {"rule_id": "new-rule", "enabled": True, "display_name": "New Rule"},
    ]
