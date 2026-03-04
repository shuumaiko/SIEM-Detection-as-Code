from main import build_app


def test_build_app_returns_usecases() -> None:
    """Smoke test to verify dependency wiring builds successfully."""
    load_tenant_uc, export_rules_uc, deploy_rules_uc, validate_tenant_uc, validate_rules_uc = (
        build_app()
    )

    assert load_tenant_uc is not None
    assert export_rules_uc is not None
    assert deploy_rules_uc is not None
    assert validate_tenant_uc is not None
    assert validate_rules_uc is not None
