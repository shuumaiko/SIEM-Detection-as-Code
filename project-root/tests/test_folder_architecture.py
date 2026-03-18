from pathlib import Path

from infrastructure.repositories.file_rule_repository import FileRuleRepository
from infrastructure.repositories.file_tenant_repository import FileTenantRepository


def test_tenant_repository_reads_deployments_from_new_structure() -> None:
    workspace_root = Path(__file__).resolve().parents[2]
    repository = FileTenantRepository(workspace_root / "tenants")

    tenant = repository.get_by_id("lab")

    assert tenant.siem_id == "splunk"
    assert tenant.rule_deployments
    assert any(item.get("dataset_id") == "cyble_alerts" for item in tenant.logsources["cyble-ti"].datasets)
    assert tenant.bindings["cyble-ti"].bindings["cyble_alerts"] == {
        "index": "cyble_alerts",
        "sourcetype": "_json",
    }
    assert tenant.bindings["checkpoint-fw"].field_mappings["traffic"]["canonical.source.ip"] == "src_ip"
    assert (workspace_root / "tenants" / "lab" / "deployments" / "rule-deployments.yaml").exists()


def test_rule_repository_reads_artifacts_from_new_structure() -> None:
    workspace_root = Path(__file__).resolve().parents[2]
    tenant_repository = FileTenantRepository(workspace_root / "tenants")
    rule_repository = FileRuleRepository(
        base_path=workspace_root / "rules",
        tenant_rules_path=workspace_root / "artifacts",
    )

    tenant = tenant_repository.get_by_id("lab")
    rules = rule_repository.list_for_tenant(tenant, include_all=True)

    assert rules
    assert any(rule.rule_id == "a123b456-c789-012d-ef34-gh567890ijkl" for rule in rules)
    assert (
        workspace_root
        / "artifacts"
        / "lab"
        / "tenant-rules"
        / "detections"
        / "network"
        / "firewall"
        / "checkpoint"
    ).exists()

