import shutil
from pathlib import Path

from domain.models.tenant import Tenant
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


def test_rule_repository_reads_render_candidates_from_current_rules() -> None:
    workspace_root = Path(__file__).resolve().parents[2]
    tenant_repository = FileTenantRepository(workspace_root / "tenants")
    rule_repository = FileRuleRepository(
        base_path=workspace_root / "rules",
        tenant_rules_path=workspace_root / "artifacts",
    )

    tenant = tenant_repository.get_by_id("lab")
    rules = rule_repository.list_render_candidates(tenant)

    assert rules
    assert any(rule.rule_id == "fa0c05b6-8ad3-468d-8231-c1cbccb64fba" for rule in rules)
    assert any(rule.source_path == "category\\antivirus\\av_hacktool.yml" for rule in rules)


def test_rule_repository_saves_and_reads_rendered_artifacts() -> None:
    workspace_root = Path(__file__).resolve().parents[2]
    test_root = workspace_root / "project-root" / ".tmp-tests" / "rule-repository"
    if test_root.exists():
        shutil.rmtree(test_root)
    test_root.mkdir(parents=True, exist_ok=True)

    rule_repository = FileRuleRepository(
        base_path=workspace_root / "rules",
        tenant_rules_path=test_root / "artifacts",
    )

    rule_repository.save_rendered_for_tenant(
        "lab",
        [
            {
                "relative_path": "category/antivirus/av_hacktool.yml",
                "document": {
                    "id": "fa0c05b6-8ad3-468d-8231-c1cbccb64fba",
                    "logsource": {"category": "antivirus", "product": "any"},
                    "x_splunk_es": {
                        "targets": {"index": "epav", "sourcetype": "eset:ra"},
                        "search_query": "index=epav sourcetype=eset:ra signature=*Hacktool*",
                    },
                },
            }
        ],
    )

    tenant = Tenant(tenant_id="lab", siem_id="splunk")
    rules = rule_repository.list_for_tenant(tenant, include_all=True)

    assert len(rules) == 1
    assert rules[0].rule_id == "fa0c05b6-8ad3-468d-8231-c1cbccb64fba"
    assert rules[0].siem_query == "index=epav sourcetype=eset:ra signature=*Hacktool*"
    assert (test_root / "artifacts" / "lab" / "tenant-rules" / "detections").exists()
