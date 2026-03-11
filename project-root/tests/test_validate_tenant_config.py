from pathlib import Path

from app.services.tenant_config_validator import TenantConfigValidator


def test_validate_tenant_accepts_fis_dataset_schema() -> None:
    workspace_root = Path(__file__).resolve().parents[2]
    validator = TenantConfigValidator(
        tenants_root=workspace_root / "tenants",
        schemas_root=workspace_root / "schema" / "tenants",
    )

    result = validator.validate("fis")

    assert result["valid"] is True
    assert result["errors"] == []
