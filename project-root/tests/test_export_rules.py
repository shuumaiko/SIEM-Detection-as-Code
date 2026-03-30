import shutil
from pathlib import Path

import yaml

from app.services.rule_artifact_service import RuleArtifactService
from app.services.rule_deployment_builder import RuleDeploymentBuilder
from app.usecases.export_rules import ExportRulesUseCase
from infrastructure.file_loader.detection_field_mapping_loader import DetectionFieldMappingLoader
from infrastructure.file_loader.execution_config_loader import ExecutionConfigLoader
from infrastructure.file_loader.registry_loader import RegistryLoader
from infrastructure.file_loader.tenant_filter_override_loader import TenantFilterOverrideLoader
from infrastructure.repositories.file_rule_repository import FileRuleRepository
from infrastructure.repositories.file_tenant_repository import FileTenantRepository


def test_gen_artifact_writes_per_rule_artifacts_and_returns_summary() -> None:
    workspace_root = Path(__file__).resolve().parents[2]
    test_root = workspace_root / "project-root" / ".tmp-tests" / "export-rules"
    if test_root.exists():
        shutil.rmtree(test_root)
    test_root.mkdir(parents=True, exist_ok=True)

    tenants_root = test_root / "tenants"
    shutil.copytree(workspace_root / "tenants" / "lab", tenants_root / "lab")
    _write_filter_override(
        tenants_root / "lab" / "overrides" / "filter" / "detections" / "fw_connection_port_23.filter.yaml",
        rule_id="2a129a58-7725-48c9-8b3a-0a2264522a68",
        rule_name="fw_connection_port_23",
        search_query=(
            'dst_port=23 NOT (action IN ("blocked", "dropped", "denied", "dropped", "deny")) '
            "NOT src IN (10.10.10.0/24)"
        ),
    )
    rules_root = test_root / "rules"
    _write_rule_fixture(
        workspace_root / "rules" / "detections" / "network" / "firewall" / "base" / "fw_connection_port_23.yml",
        rules_root / "detections" / "network" / "firewall" / "base" / "fw_connection_port_23.yml",
        status="stable",
    )
    _write_rule_fixture(
        workspace_root / "rules" / "detections" / "network" / "firewall" / "base" / "fw_external_connection.yml",
        rules_root / "detections" / "network" / "firewall" / "base" / "fw_external_connection.yml",
        status="stable",
    )
    _write_rule_fixture(
        workspace_root / "rules" / "analysts" / "network" / "firewall" / "base" / "net_fw_request_reached_over_threshold.yaml",
        rules_root / "analysts" / "network" / "firewall" / "base" / "net_fw_request_reached_over_threshold.yaml",
        status="stable",
    )
    _write_rule_fixture(
        workspace_root / "rules" / "detections" / "category" / "antivirus" / "av_hacktool.yml",
        rules_root / "detections" / "category" / "antivirus" / "av_hacktool.yml",
        status="test",
    )
    _set_rule_enabled_state(
        tenants_root / "lab" / "deployments" / "rule-deployments.yaml",
        "2a129a58-7725-48c9-8b3a-0a2264522a68",
        False,
    )

    tenant_repository = FileTenantRepository(tenants_root)
    rule_repository = FileRuleRepository(
        base_path=rules_root,
        tenant_rules_path=test_root / "artifacts",
    )
    deployment_builder = RuleDeploymentBuilder(
        registry_loader=RegistryLoader(workspace_root / "mappings" / "logsources"),
        detection_field_mapping_loader=DetectionFieldMappingLoader(
            workspace_root / "mappings" / "detections"
        ),
        tenant_filter_override_loader=TenantFilterOverrideLoader(tenants_root),
    )
    artifact_service = RuleArtifactService(
        execution_loader=ExecutionConfigLoader(
            execution_root=workspace_root / "execution",
            tenants_root=tenants_root,
        )
    )
    use_case = ExportRulesUseCase(
        tenant_repository=tenant_repository,
        rule_repository=rule_repository,
        deployment_builder=deployment_builder,
        artifact_service=artifact_service,
    )

    rendered_rules, summary = use_case.prepare_export("lab")

    rendered_ids = [item["id"] for item in rendered_rules]
    assert rendered_ids == [
        "2a129a58-7725-48c9-8b3a-0a2264522a68",
        "faee897b-2394-45cf-ae5d-0379476fbf3e",
    ]

    firewall_artifact = (
        test_root
        / "artifacts"
        / "lab"
        / "splunk"
        / "detections"
        / "network"
        / "firewall"
        / "base"
        / "fw_connection_port_23.yml"
    )
    analyst_artifact = (
        test_root
        / "artifacts"
        / "lab"
        / "splunk"
        / "analysts"
        / "network"
        / "firewall"
        / "base"
        / "net_fw_request_reached_over_threshold.yaml"
    )
    base_artifact = (
        test_root
        / "artifacts"
        / "lab"
        / "splunk"
        / "detections"
        / "network"
        / "firewall"
        / "base"
        / "fw_external_connection.yml"
    )
    summary_artifact = test_root / "artifacts" / "lab" / "export-summary.yml"
    deployment_manifest = tenants_root / "lab" / "deployments" / "rule-deployments.yaml"

    assert firewall_artifact.exists()
    assert analyst_artifact.exists()
    assert not base_artifact.exists()
    assert not summary_artifact.exists()
    assert deployment_manifest.exists()

    with open(firewall_artifact, "r", encoding="utf-8") as file:
        firewall_doc = yaml.safe_load(file)
    with open(analyst_artifact, "r", encoding="utf-8") as file:
        analyst_doc = yaml.safe_load(file)
    with open(firewall_artifact, "r", encoding="utf-8") as file:
        firewall_raw_text = file.read()
    with open(deployment_manifest, "r", encoding="utf-8") as file:
        deployment_doc = yaml.safe_load(file)

    deployment_items = deployment_doc["rule_deployments_by_siem"]["splunk"]
    deployment_ids = {item["rule_id"] for item in deployment_items}

    assert summary == {
        "tenant_id": "lab",
        "siem_id": "splunk",
        "generated_artifact_count": 2,
        "rule_count_by_type": {"analyst": 1, "detection": 1},
        "deployed_device_ids": ["checkpoint-fw"],
        "deployed_dataset_ids": ["traffic"],
        "deployed_logsources": [
            {
                "category": "firewall",
                "product": "any",
                "service": "traffic",
                "rule_count": 2,
                "device_ids": ["checkpoint-fw"],
                "dataset_ids": ["traffic"],
                "indexes": ["checkpoint"],
                "sourcetypes": ["cp_log"],
            }
        ],
        "artifact_root": "artifacts/lab/splunk",
        "deployment_manifest_path": "tenants/lab/deployments/rule-deployments.yaml",
    }
    assert firewall_doc["artifact_type"] == "tenant_rule"
    assert firewall_doc["tenant_id"] == "lab"
    assert firewall_doc["siem_id"] == "splunk"
    assert firewall_doc["source_rule"]["rule_id"] == "2a129a58-7725-48c9-8b3a-0a2264522a68"
    assert firewall_doc["display_name"].startswith("checkpoint-fw - ")
    assert firewall_doc["x_splunk_es"]["targets"]["index"] == "checkpoint"
    assert firewall_doc["x_splunk_es"]["targets"]["sourcetype"] == "cp_log"
    assert firewall_doc["x_splunk_es"]["targets"]["enabled"] is False
    assert firewall_doc["x_splunk_es"]["targets"]["schedule_cron"] == "*/30 * * * *"
    assert firewall_doc["x_splunk_es"]["search_query"]
    assert "_field_bindings" not in firewall_doc["x_splunk_es"]["targets"]["ingest_targets"][0]
    assert "\n\n\n" not in firewall_raw_text
    assert "$index$" not in firewall_doc["x_splunk_es"]["search_query"]
    assert "$sourcetype$" not in firewall_doc["x_splunk_es"]["search_query"]
    assert "service=23" in firewall_doc["x_splunk_es"]["search_query"]
    assert "src_ip IN (10.10.10.0/24)" in firewall_doc["x_splunk_es"]["search_query"]
    assert "dst_port=23" not in firewall_doc["x_splunk_es"]["search_query"]
    assert "src IN (10.10.10.0/24)" not in firewall_doc["x_splunk_es"]["search_query"]

    assert analyst_doc["artifact_type"] == "tenant_rule"
    assert analyst_doc["source_rule"]["rule_id"] == "faee897b-2394-45cf-ae5d-0379476fbf3e"
    assert analyst_doc["display_name"].startswith("checkpoint-fw - ")
    assert analyst_doc["x_splunk_es"]["targets"]["enabled"] is True
    assert "faee897b-2394-45cf-ae5d-0379476fbf3e" in deployment_ids
    assert "2a129a58-7725-48c9-8b3a-0a2264522a68" in deployment_ids
    assert "e00cc3a0-d141-4495-b67c-390162eed27a" not in deployment_ids


def test_gen_artifact_splits_multi_logsource_rules_per_device() -> None:
    workspace_root = Path(__file__).resolve().parents[2]
    test_root = workspace_root / "project-root" / ".tmp-tests" / "export-rules-multi-target"
    if test_root.exists():
        shutil.rmtree(test_root)
    test_root.mkdir(parents=True, exist_ok=True)

    tenants_root = test_root / "tenants"
    shutil.copytree(workspace_root / "tenants" / "lab", tenants_root / "lab")
    eset_fields_path = tenants_root / "lab" / "bindings" / "fields" / "eset-ra.fields.yml"
    eset_fields_path.parent.mkdir(parents=True, exist_ok=True)
    eset_fields_path.write_text(
        "\n".join(
            [
                "schema_version: 1.0",
                "tenant_id: lab",
                "siem_id: splunk",
                "device_id: eset-ra",
                "default_field_mapping:",
                "  time: _time",
                "  canonical.event.action: action_taken",
                "  malware.name: threat_name",
                "  file.name: file_name",
                "  file.path: file_path",
                "  file.hashes: file_hash",
                "  device.hostname: hostname",
                "  device.ip: ipv4",
                "  user.name: user",
                "  process.name: processname",
                "",
            ]
        ),
        encoding="utf-8",
    )
    rules_root = test_root / "rules"
    _write_rule_fixture(
        workspace_root / "rules" / "detections" / "category" / "antivirus" / "av_password_dumper.yml",
        rules_root / "detections" / "category" / "antivirus" / "av_password_dumper.yml",
        status="stable",
    )

    tenant_repository = FileTenantRepository(tenants_root)
    rule_repository = FileRuleRepository(
        base_path=rules_root,
        tenant_rules_path=test_root / "artifacts",
    )
    deployment_builder = RuleDeploymentBuilder(
        registry_loader=RegistryLoader(workspace_root / "mappings" / "logsources"),
        detection_field_mapping_loader=DetectionFieldMappingLoader(
            workspace_root / "mappings" / "detections"
        ),
        tenant_filter_override_loader=TenantFilterOverrideLoader(tenants_root),
    )
    artifact_service = RuleArtifactService(
        execution_loader=ExecutionConfigLoader(
            execution_root=workspace_root / "execution",
            tenants_root=tenants_root,
        )
    )
    use_case = ExportRulesUseCase(
        tenant_repository=tenant_repository,
        rule_repository=rule_repository,
        deployment_builder=deployment_builder,
        artifact_service=artifact_service,
    )

    rendered_rules, summary = use_case.prepare_export("lab")

    rendered_ids = {item["id"] for item in rendered_rules}
    assert rendered_ids == {
        "78cc2dd2-7d20-4d32-93ff-057084c38b93::eset-ra::eset-ra-alerts",
        "78cc2dd2-7d20-4d32-93ff-057084c38b93::mcafee-epo::mcafee-epo-syslog",
    }
    assert {item["display_name"] for item in rendered_rules} == {
        "eset-ra - Antivirus Password Dumper Detection",
        "mcafee-epo - Antivirus Password Dumper Detection",
    }

    eset_artifact = (
        test_root
        / "artifacts"
        / "lab"
        / "splunk"
        / "detections"
        / "category"
        / "antivirus"
        / "av_password_dumper__eset-ra__eset-ra-alerts.yml"
    )
    mcafee_artifact = (
        test_root
        / "artifacts"
        / "lab"
        / "splunk"
        / "detections"
        / "category"
        / "antivirus"
        / "av_password_dumper__mcafee-epo__mcafee-epo-syslog.yml"
    )
    deployment_manifest = tenants_root / "lab" / "deployments" / "rule-deployments.yaml"

    assert eset_artifact.exists()
    assert mcafee_artifact.exists()
    assert summary["generated_artifact_count"] == 2
    assert summary["deployed_device_ids"] == ["eset-ra", "mcafee-epo"]

    with open(eset_artifact, "r", encoding="utf-8") as file:
        eset_doc = yaml.safe_load(file)
    with open(mcafee_artifact, "r", encoding="utf-8") as file:
        mcafee_doc = yaml.safe_load(file)
    with open(deployment_manifest, "r", encoding="utf-8") as file:
        deployment_doc = yaml.safe_load(file)

    assert eset_doc["id"] == "78cc2dd2-7d20-4d32-93ff-057084c38b93::eset-ra::eset-ra-alerts"
    assert eset_doc["display_name"] == "eset-ra - Antivirus Password Dumper Detection"
    assert eset_doc["x_splunk_es"]["targets"]["device_id"] == "eset-ra"
    assert eset_doc["x_splunk_es"]["targets"]["dataset_id"] == "eset-ra-alerts"
    assert eset_doc["x_splunk_es"]["targets"]["sourcetype"] == "eset:ra"
    assert "_field_bindings" not in eset_doc["x_splunk_es"]["targets"]["ingest_targets"][0]
    assert "threat_name=" in eset_doc["x_splunk_es"]["search_query"]
    assert "values(file_name) as file_name" in eset_doc["x_splunk_es"]["search_query"]
    assert "values(processname) as processname" in eset_doc["x_splunk_es"]["search_query"]

    assert mcafee_doc["id"] == "78cc2dd2-7d20-4d32-93ff-057084c38b93::mcafee-epo::mcafee-epo-syslog"
    assert mcafee_doc["display_name"] == "mcafee-epo - Antivirus Password Dumper Detection"
    assert mcafee_doc["x_splunk_es"]["targets"]["device_id"] == "mcafee-epo"
    assert mcafee_doc["x_splunk_es"]["targets"]["dataset_id"] == "mcafee-epo-syslog"
    assert mcafee_doc["x_splunk_es"]["targets"]["sourcetype"] == "mcafee:epo:syslog"
    assert "_field_bindings" not in mcafee_doc["x_splunk_es"]["targets"]["ingest_targets"][0]
    assert "signature=" in mcafee_doc["x_splunk_es"]["search_query"]
    assert "values(TargetName) as file_name" in mcafee_doc["x_splunk_es"]["search_query"]
    assert "values(source_process_name) as processname" in mcafee_doc["x_splunk_es"]["search_query"]

    deployment_ids = {
        item["rule_id"] for item in deployment_doc["rule_deployments_by_siem"]["splunk"]
    }
    assert deployment_ids == rendered_ids


def test_gen_artifact_skips_targets_without_field_mapping() -> None:
    workspace_root = Path(__file__).resolve().parents[2]
    test_root = workspace_root / "project-root" / ".tmp-tests" / "export-rules-require-fields"
    if test_root.exists():
        shutil.rmtree(test_root)
    test_root.mkdir(parents=True, exist_ok=True)

    tenants_root = test_root / "tenants"
    shutil.copytree(workspace_root / "tenants" / "lab", tenants_root / "lab")
    rules_root = test_root / "rules"
    _write_rule_fixture(
        workspace_root / "rules" / "detections" / "category" / "antivirus" / "av_password_dumper.yml",
        rules_root / "detections" / "category" / "antivirus" / "av_password_dumper.yml",
        status="stable",
    )

    tenant_repository = FileTenantRepository(tenants_root)
    rule_repository = FileRuleRepository(
        base_path=rules_root,
        tenant_rules_path=test_root / "artifacts",
    )
    deployment_builder = RuleDeploymentBuilder(
        registry_loader=RegistryLoader(workspace_root / "mappings" / "logsources"),
        detection_field_mapping_loader=DetectionFieldMappingLoader(
            workspace_root / "mappings" / "detections"
        ),
        tenant_filter_override_loader=TenantFilterOverrideLoader(tenants_root),
    )
    artifact_service = RuleArtifactService(
        execution_loader=ExecutionConfigLoader(
            execution_root=workspace_root / "execution",
            tenants_root=tenants_root,
        )
    )
    use_case = ExportRulesUseCase(
        tenant_repository=tenant_repository,
        rule_repository=rule_repository,
        deployment_builder=deployment_builder,
        artifact_service=artifact_service,
    )

    rendered_rules, summary = use_case.prepare_export("lab")

    assert [item["id"] for item in rendered_rules] == [
        "78cc2dd2-7d20-4d32-93ff-057084c38b93"
    ]
    assert rendered_rules[0]["display_name"] == "mcafee-epo - Antivirus Password Dumper Detection"
    assert rendered_rules[0]["targets"]["device_id"] == "mcafee-epo"
    assert rendered_rules[0]["targets"]["dataset_id"] == "mcafee-epo-syslog"
    assert summary["generated_artifact_count"] == 1
    assert summary["deployed_device_ids"] == ["mcafee-epo"]
    assert summary["deployed_dataset_ids"] == ["mcafee-epo-syslog"]

    mcafee_artifact = (
        test_root
        / "artifacts"
        / "lab"
        / "splunk"
        / "detections"
        / "category"
        / "antivirus"
        / "av_password_dumper.yml"
    )
    eset_artifact = (
        test_root
        / "artifacts"
        / "lab"
        / "splunk"
        / "detections"
        / "category"
        / "antivirus"
        / "av_password_dumper__eset-ra__eset-ra-alerts.yml"
    )
    assert mcafee_artifact.exists()
    assert not eset_artifact.exists()


def test_gen_artifact_skips_targets_without_required_query_field_bindings() -> None:
    workspace_root = Path(__file__).resolve().parents[2]
    test_root = workspace_root / "project-root" / ".tmp-tests" / "export-rules-require-query-fields"
    if test_root.exists():
        shutil.rmtree(test_root)
    test_root.mkdir(parents=True, exist_ok=True)

    tenants_root = test_root / "tenants"
    shutil.copytree(workspace_root / "tenants" / "lab", tenants_root / "lab")
    eset_fields_path = tenants_root / "lab" / "bindings" / "fields" / "eset-ra.fields.yml"
    eset_fields_path.parent.mkdir(parents=True, exist_ok=True)
    eset_fields_path.write_text(
        "\n".join(
            [
                "schema_version: 1.0",
                "tenant_id: lab",
                "siem_id: splunk",
                "device_id: eset-ra",
                "default_field_mapping:",
                "  time: _time",
                "  canonical.event.action: action_taken",
                "  malware.name: threat_name",
                "  device.hostname: hostname",
                "  device.ip: ipv4",
                "",
            ]
        ),
        encoding="utf-8",
    )
    rules_root = test_root / "rules"
    _write_rule_fixture(
        workspace_root / "rules" / "detections" / "category" / "antivirus" / "av_password_dumper.yml",
        rules_root / "detections" / "category" / "antivirus" / "av_password_dumper.yml",
        status="stable",
    )

    tenant_repository = FileTenantRepository(tenants_root)
    rule_repository = FileRuleRepository(
        base_path=rules_root,
        tenant_rules_path=test_root / "artifacts",
    )
    deployment_builder = RuleDeploymentBuilder(
        registry_loader=RegistryLoader(workspace_root / "mappings" / "logsources"),
        detection_field_mapping_loader=DetectionFieldMappingLoader(
            workspace_root / "mappings" / "detections"
        ),
        tenant_filter_override_loader=TenantFilterOverrideLoader(tenants_root),
    )
    artifact_service = RuleArtifactService(
        execution_loader=ExecutionConfigLoader(
            execution_root=workspace_root / "execution",
            tenants_root=tenants_root,
        )
    )
    use_case = ExportRulesUseCase(
        tenant_repository=tenant_repository,
        rule_repository=rule_repository,
        deployment_builder=deployment_builder,
        artifact_service=artifact_service,
    )

    rendered_rules, summary = use_case.prepare_export("lab")

    assert [item["id"] for item in rendered_rules] == [
        "78cc2dd2-7d20-4d32-93ff-057084c38b93"
    ]
    assert summary["generated_artifact_count"] == 1
    assert summary["deployed_device_ids"] == ["mcafee-epo"]

    eset_artifact = (
        test_root
        / "artifacts"
        / "lab"
        / "splunk"
        / "detections"
        / "category"
        / "antivirus"
        / "av_password_dumper__eset-ra__eset-ra-alerts.yml"
    )
    assert not eset_artifact.exists()


def _write_rule_fixture(source_path: Path, target_path: Path, status: str) -> None:
    """Copy one source rule into a temporary rules root with an overridden status."""
    with open(source_path, "r", encoding="utf-8") as file:
        document = yaml.safe_load(file)

    document["status"] = status
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with open(target_path, "w", encoding="utf-8") as file:
        yaml.safe_dump(document, file, sort_keys=False, allow_unicode=True, width=4096)


def _set_rule_enabled_state(deployment_path: Path, rule_id: str, enabled: bool) -> None:
    """Update one deployment entry in a copied tenant manifest for regression tests."""
    with open(deployment_path, "r", encoding="utf-8") as file:
        document = yaml.safe_load(file)

    deployments = ((document or {}).get("rule_deployments_by_siem") or {}).get("splunk") or []
    for item in deployments:
        if isinstance(item, dict) and item.get("rule_id") == rule_id:
            item["enabled"] = enabled

    with open(deployment_path, "w", encoding="utf-8") as file:
        yaml.safe_dump(document, file, sort_keys=False, allow_unicode=True, width=4096)


def _write_filter_override(
    target_path: Path,
    rule_id: str,
    rule_name: str,
    search_query: str,
) -> None:
    """Write one tenant filter override used by render regression tests."""
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with open(target_path, "w", encoding="utf-8") as file:
        yaml.safe_dump(
            {
                "tenant_id": "lab",
                "rule_id": rule_id,
                "rule_name": rule_name,
                "query_modifiers": {
                    "splunk": {
                        "search_query": search_query,
                    }
                },
            },
            file,
            sort_keys=False,
            allow_unicode=True,
            width=4096,
        )
