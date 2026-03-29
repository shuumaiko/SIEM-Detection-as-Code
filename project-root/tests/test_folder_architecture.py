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
    assert tenant.bindings["checkpoint-fw"].field_mappings["traffic"]["src_endpoint.ip"] == "src_ip"
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
    assert any(rule.rule_id == "faee897b-2394-45cf-ae5d-0379476fbf3e" for rule in rules)
    assert any(rule.source_path == "detections\\category\\antivirus\\av_hacktool.yml" for rule in rules)
    assert any(
        rule.source_path == "analysts\\network\\firewall\\base\\net_fw_request_reached_over_threshold.yaml"
        for rule in rules
    )


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
                "relative_path": "detections/category/antivirus/av_hacktool.yml",
                "document": {
                    "artifact_schema_version": 1.0,
                    "artifact_type": "tenant_rule",
                    "tenant_id": "lab",
                    "siem_id": "splunk",
                    "source_rule": {
                        "rule_id": "fa0c05b6-8ad3-468d-8231-c1cbccb64fba",
                        "rule_name": "av_hacktool",
                        "rule_type": "detection",
                        "source_path": "rules/detections/category/antivirus/av_hacktool.yml",
                        "status": "stable",
                        "level": "medium",
                        "version": "1.0.0",
                    },
                    "display_name": "mcafee-epo - Antivirus Hacktool Detection",
                    "metadata": {
                        "tags": ["attack.execution"],
                        "owner": "team-detection",
                        "last_rendered": "2026-03-29T00:00:00Z",
                    },
                    "x_splunk_es": {
                        "targets": {
                            "ingest_targets": [
                                {
                                    "device_id": "mcafee-epo",
                                    "dataset_id": "mcafee-epo-syslog",
                                    "index": "epo",
                                    "sourcetype": "mcafee:epo:syslog",
                                }
                            ],
                            "index": "epo",
                            "sourcetype": "mcafee:epo:syslog",
                        },
                        "search_query": "index=epo sourcetype=mcafee:epo:syslog signature=*Hacktool*",
                    },
                },
            }
        ],
    )

    tenant = Tenant(tenant_id="lab", siem_id="splunk")
    rules = rule_repository.list_for_tenant(tenant, include_all=True)

    assert len(rules) == 1
    assert rules[0].rule_id == "fa0c05b6-8ad3-468d-8231-c1cbccb64fba"
    assert rules[0].siem_query == "index=epo sourcetype=mcafee:epo:syslog signature=*Hacktool*"
    assert (
        test_root
        / "artifacts"
        / "lab"
        / "tenant-rules"
        / "detections"
        / "category"
        / "antivirus"
        / "av_hacktool.yml"
    ).exists()
