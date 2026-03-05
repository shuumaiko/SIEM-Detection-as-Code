from pathlib import Path

from app.services.rule_format_validator import RuleFormatValidator
from app.services.rule_deployment_builder import RuleDeploymentBuilder
from app.services.tenant_config_validator import TenantConfigValidator
from app.usecases.deploy_rules import DeployRulesUseCase
from app.usecases.export_rules import ExportRulesUseCase
from app.usecases.load_tenant import LoadTenantUseCase
from app.usecases.validate_rule_format import ValidateRuleFormatUseCase
from app.usecases.validate_tenant_config import ValidateTenantConfigUseCase
from infrastructure.repositories.file_rule_repository import FileRuleRepository
from infrastructure.repositories.file_tenant_repository import FileTenantRepository
from infrastructure.file_loader.registry_loader import RegistryLoader
from infrastructure.siem.splunk_adapter import SplunkAdapter
from interfaces.cli import run_cli


def build_app() -> tuple[
    LoadTenantUseCase,
    ExportRulesUseCase,
    DeployRulesUseCase,
    ValidateTenantConfigUseCase,
    ValidateRuleFormatUseCase,
]:
    """Wire repositories/adapters and return use case instances."""
    workspace_root = Path(__file__).resolve().parent.parent

    tenant_repo = FileTenantRepository(base_path=workspace_root / "tenants")
    rule_repo = FileRuleRepository(
        base_path=workspace_root / "rules",
        tenant_rules_path=workspace_root / "tenant-rules",
    )
    registry_loader = RegistryLoader(root=workspace_root / "logsource-mapping-registry")
    deployment_builder = RuleDeploymentBuilder(registry_loader=registry_loader)
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
        ExportRulesUseCase(tenant_repo, rule_repo, deployment_builder),
        DeployRulesUseCase(tenant_repo, rule_repo, siem_adapter),
        ValidateTenantConfigUseCase(tenant_validator),
        ValidateRuleFormatUseCase(rule_validator),
    )


def main(argv: list[str] | None = None) -> None:
    """Run CLI entrypoint for SIEM-DaC commands."""
    run_cli(build_app_fn=build_app, argv=argv)


if __name__ == "__main__":
    main()
