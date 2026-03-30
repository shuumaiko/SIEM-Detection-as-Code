# Project Root Current Context

## Repository Truth

- Prefer `docs/architecture/project-architecture.md` when the documented repository model conflicts with older assumptions inside `project-root/`.
- Treat `project-root/` as a Clean Architecture-oriented skeleton that already exposes useful boundaries, but still contains transitional logic and compatibility behavior.
- Treat all repository folders named `legacy/` as historical-only concepts. Do not use them to infer the real architecture, the default runtime path, or the current business contract unless the user explicitly asks for legacy compatibility or migration work.

## Current Main Flows

### `load-tenant`

Flow:

`main.build_app()` -> `interfaces.cli.run_cli()` -> `LoadTenantUseCase.execute()` -> `TenantService.load_tenant()` -> `FileTenantRepository.get_by_id()`

Business purpose:

Load a tenant aggregate from on-disk YAML so later flows can validate, export, or deploy against a concrete tenant context.

### `export-rules`

Flow:

`main.build_app()` -> `interfaces.cli.run_cli()` -> `ExportRulesUseCase.execute()` -> `TenantRepository.get_by_id()` -> `RuleService.load_rules_for_tenant()` -> `ExportService.export_rules()` -> `RuleDeploymentBuilder.build()` -> `TenantRepository.save_rule_deployments()`

Business purpose:

Read tenant-ready rules, enrich deployment targets, and persist `rule-deployments.yaml`.

### `deploy-rules`

Flow:

`main.build_app()` -> `interfaces.cli.run_cli()` -> `DeployRulesUseCase.execute()` -> `TenantRepository.get_by_id()` or exported payload -> `DeploymentService.deploy()` -> `BaseSIEMAdapter.deploy_rules()`

Business purpose:

Turn exported or prebuilt rules into an adapter call for the target SIEM.

### `validate-tenant`

Flow:

`main.build_app()` -> `interfaces.cli.run_cli()` -> `ValidateTenantConfigUseCase.execute()` -> `TenantConfigValidator.validate()`

Business purpose:

Validate tenant YAML structure, schema compliance, cross-file references, and deployment manifest consistency.

### `validate-rules`

Flow:

`main.build_app()` -> `interfaces.cli.run_cli()` -> `ValidateRuleFormatUseCase.execute()` -> `RuleFormatValidator.validate()`

Business purpose:

Validate rule YAML format and schema compatibility for detection and analyst rule files.

## Important Transitional Patterns

- Several use cases and services are thin pass-through wrappers. Do not add more layers unless the task gains clear business value.
- `FileTenantRepository` and `FileRuleRepository` may still contain compatibility helpers for older layouts inside active code. Preserve only the compatibility that is already part of current runtime contracts; do not reintroduce or depend on on-disk `legacy/` folders unless the user explicitly requests it.
- `RuleDeploymentBuilder` currently owns target resolution, deployment payload shaping, and query placeholder replacement such as `$INDEX$` and `$SOURCETYPE$`.
- Validators are self-contained application services that walk files, load schemas, and emit structured result dictionaries.

## Layer Placement Heuristics

- Keep CLI argument parsing and command dispatch in `interfaces/`.
- Keep scenario orchestration in `app/usecases/`.
- Keep reusable business logic in `app/services/`.
- Keep entities and repository contracts in `domain/`.
- Keep filesystem, loaders, adapters, and external integration details in `infrastructure/`.

## Current Testing Signals

- `project-root/tests/test_smoke.py` verifies dependency wiring.
- `project-root/tests/test_folder_architecture.py` verifies repository path assumptions and deployment loading.
- `project-root/tests/test_rule_deployment_builder.py` covers deployment payload behavior.
- `project-root/tests/test_validate_tenant_config.py` covers tenant validation against current sample data.

Add or update nearby tests whenever a change modifies branching, normalization, fallback behavior, or file layout assumptions.
