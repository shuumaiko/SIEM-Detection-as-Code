import shutil
from pathlib import Path

import yaml

from app.services.rule_artifact_service import RuleArtifactService
from app.services.rule_deployment_builder import RuleDeploymentBuilder
from app.usecases.export_rules import ExportRulesUseCase
from infrastructure.file_loader.execution_config_loader import ExecutionConfigLoader
from infrastructure.file_loader.registry_loader import RegistryLoader
from infrastructure.repositories.file_rule_repository import FileRuleRepository
from infrastructure.repositories.file_tenant_repository import FileTenantRepository


def test_export_rules_renders_source_rules_into_artifacts() -> None:
    workspace_root = Path(__file__).resolve().parents[2]
    test_root = workspace_root / "project-root" / ".tmp-tests" / "export-rules"
    if test_root.exists():
        shutil.rmtree(test_root)
    test_root.mkdir(parents=True, exist_ok=True)

    tenants_root = test_root / "tenants"
    shutil.copytree(workspace_root / "tenants" / "lab", tenants_root / "lab")

    tenant_repository = FileTenantRepository(tenants_root)
    rule_repository = FileRuleRepository(
        base_path=workspace_root / "rules",
        tenant_rules_path=test_root / "artifacts",
    )
    deployment_builder = RuleDeploymentBuilder(
        registry_loader=RegistryLoader(workspace_root / "mappings" / "logsources")
    )
    artifact_service = RuleArtifactService(
        execution_loader=ExecutionConfigLoader(
            execution_root=workspace_root / "legacy" / "execution",
            tenants_root=tenants_root,
        )
    )
    use_case = ExportRulesUseCase(
        tenant_repository=tenant_repository,
        rule_repository=rule_repository,
        deployment_builder=deployment_builder,
        artifact_service=artifact_service,
    )

    rendered_rules = use_case.execute("lab")

    assert any(item["id"] == "fa0c05b6-8ad3-468d-8231-c1cbccb64fba" for item in rendered_rules)
    assert any(item["id"] == "2a129a58-7725-48c9-8b3a-0a2264522a68" for item in rendered_rules)

    antivirus_artifact = (
        test_root
        / "artifacts"
        / "lab"
        / "tenant-rules"
        / "detections"
        / "category"
        / "antivirus"
        / "av_hacktool.yml"
    )
    firewall_artifact = (
        test_root
        / "artifacts"
        / "lab"
        / "tenant-rules"
        / "detections"
        / "network"
        / "firewall"
        / "base"
        / "fw_connection_port_23.yaml"
    )
    deployment_manifest = tenants_root / "lab" / "deployments" / "rule-deployments.yaml"

    assert antivirus_artifact.exists()
    assert firewall_artifact.exists()
    assert deployment_manifest.exists()

    with open(antivirus_artifact, "r", encoding="utf-8") as file:
        antivirus_doc = yaml.safe_load(file)
    with open(firewall_artifact, "r", encoding="utf-8") as file:
        firewall_doc = yaml.safe_load(file)
    with open(deployment_manifest, "r", encoding="utf-8") as file:
        deployment_doc = yaml.safe_load(file)

    antivirus_targets = antivirus_doc["x_splunk_es"]["targets"]
    firewall_query = firewall_doc["x_splunk_es"]["search_query"]
    deployment_ids = {item["rule_id"] for item in deployment_doc["rule_deployments_by_siem"]["splunk"]}

    assert antivirus_targets["index"] == "epav"
    assert antivirus_targets["notable"]["severity"] == "medium"
    assert antivirus_targets["notable"]["risk_score"] == 20
    assert antivirus_targets["schedule_cron"] == "*/30 * * * *"
    assert "index=checkpoint" in firewall_query
    assert "sourcetype=cp_log" in firewall_query
    assert "$index$" not in firewall_query
    assert "$sourcetype$" not in firewall_query
    assert "fa0c05b6-8ad3-468d-8231-c1cbccb64fba" in deployment_ids
    assert "2a129a58-7725-48c9-8b3a-0a2264522a68" in deployment_ids
