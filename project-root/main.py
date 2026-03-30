from __future__ import annotations

import sys
from pathlib import Path

from interfaces.cli import run_cli


def _format_missing_dependency_error(exc: ModuleNotFoundError) -> str:
    """Format an actionable startup error for missing Python modules.

    Args:
        exc: The import exception raised while wiring the CLI application.

    Returns:
        A human-readable message with the missing module name and a suggested
        install command for the active Python interpreter.

    Side effects:
        None.
    """
    requirements_path = Path(__file__).resolve().parent / "requirements.txt"
    missing_module = exc.name or "<unknown>"
    install_command = f'"{sys.executable}" -m pip install -r "{requirements_path}"'
    return (
        f"Missing Python module '{missing_module}' while starting the SIEM-DaC CLI.\n"
        "If this module is part of the project dependencies, install them with:\n"
        f"  {install_command}\n"
        f"Original import error: {exc}"
    )


def build_app() -> tuple[object, object, object, object, object]:
    """Wire repositories and adapters, then return the CLI use cases.

    Returns:
        A tuple containing the tenant loading, export, deploy, tenant
        validation, and rule validation use cases in CLI dispatch order.

    Side effects:
        Imports the application wiring modules and resolves repository paths
        relative to the repository workspace root.
    """
    from app.services.rule_artifact_service import RuleArtifactService
    from app.services.rule_deployment_builder import RuleDeploymentBuilder
    from app.services.rule_format_validator import RuleFormatValidator
    from app.services.tenant_config_validator import TenantConfigValidator
    from app.usecases.deploy_rules import DeployRulesUseCase
    from app.usecases.export_rules import ExportRulesUseCase
    from app.usecases.load_tenant import LoadTenantUseCase
    from app.usecases.validate_rule_format import ValidateRuleFormatUseCase
    from app.usecases.validate_tenant_config import ValidateTenantConfigUseCase
    from infrastructure.file_loader.detection_field_mapping_loader import (
        DetectionFieldMappingLoader,
    )
    from infrastructure.file_loader.execution_config_loader import ExecutionConfigLoader
    from infrastructure.file_loader.registry_loader import RegistryLoader
    from infrastructure.file_loader.tenant_filter_override_loader import (
        TenantFilterOverrideLoader,
    )
    from infrastructure.repositories.file_rule_repository import FileRuleRepository
    from infrastructure.repositories.file_tenant_repository import FileTenantRepository
    from infrastructure.siem.splunk_adapter import SplunkAdapter

    workspace_root = Path(__file__).resolve().parent.parent

    tenant_repo = FileTenantRepository(base_path=workspace_root / "tenants")
    rule_repo = FileRuleRepository(
        base_path=workspace_root / "rules",
        tenant_rules_path=workspace_root / "artifacts",
    )
    registry_loader = RegistryLoader(root=workspace_root / "mappings" / "logsources")
    detection_field_mapping_loader = DetectionFieldMappingLoader(
        mappings_root=workspace_root / "mappings" / "detections"
    )
    execution_loader = ExecutionConfigLoader(
        execution_root=workspace_root / "execution",
        tenants_root=workspace_root / "tenants",
    )
    tenant_filter_override_loader = TenantFilterOverrideLoader(
        tenants_root=workspace_root / "tenants"
    )
    deployment_builder = RuleDeploymentBuilder(
        registry_loader=registry_loader,
        detection_field_mapping_loader=detection_field_mapping_loader,
        tenant_filter_override_loader=tenant_filter_override_loader,
    )
    artifact_service = RuleArtifactService(execution_loader=execution_loader)
    siem_adapter = SplunkAdapter()
    tenant_validator = TenantConfigValidator(
        tenants_root=workspace_root / "tenants",
        schemas_root=workspace_root / "schema" / "tenants",
    )
    rule_validator = RuleFormatValidator(
        rules_root=workspace_root / "rules",
        schemas_root=workspace_root / "schema" / "rules",
    )

    return (
        LoadTenantUseCase(tenant_repo),
        ExportRulesUseCase(tenant_repo, rule_repo, deployment_builder, artifact_service),
        DeployRulesUseCase(tenant_repo, rule_repo, siem_adapter),
        ValidateTenantConfigUseCase(tenant_validator),
        ValidateRuleFormatUseCase(rule_validator),
    )


def main(argv: list[str] | None = None) -> None:
    """Run the SIEM-DaC CLI entrypoint.

    Args:
        argv: Optional argument vector passed through to the CLI parser.

    Side effects:
        Parses CLI arguments, wires application dependencies, executes the
        selected use case, and writes command output to stdout or stderr.
    """
    try:
        run_cli(build_app_fn=build_app, argv=argv)
    except ModuleNotFoundError as exc:
        raise SystemExit(_format_missing_dependency_error(exc)) from exc


if __name__ == "__main__":
    main()
