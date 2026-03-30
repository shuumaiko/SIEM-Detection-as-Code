import argparse
import json
from typing import Callable


def create_parser() -> argparse.ArgumentParser:
    """Create CLI parser with supported commands."""
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="SIEM-DaC CLI skeleton",
    )
    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        help="Available commands",
    )

    load_tenant = subparsers.add_parser("load-tenant", help="Load tenant configuration")
    load_tenant.add_argument("--tenant-id", required=True, help="Tenant identifier")

    gen_artifact = subparsers.add_parser(
        "gen-artifact",
        help="Generate tenant rule artifacts and print summary metadata",
    )
    gen_artifact.add_argument("--tenant-id", required=True, help="Tenant identifier")

    export_rules = subparsers.add_parser(
        "export-rules",
        help="Legacy alias for gen-artifact",
    )
    export_rules.add_argument("--tenant-id", required=True, help="Tenant identifier")

    deploy_rules = subparsers.add_parser("deploy-rules", help="Deploy rules to tenant SIEM")
    deploy_rules.add_argument("--tenant-id", required=True, help="Tenant identifier")

    validate_tenant = subparsers.add_parser(
        "validate-tenant",
        help="Validate tenant config files and cross references",
    )
    validate_tenant.add_argument("--tenant-id", required=True, help="Tenant identifier")

    validate_rules = subparsers.add_parser(
        "validate-rules",
        help="Validate detection rule format (--all or --since dd/mm/yyyy)",
    )
    scope_group = validate_rules.add_mutually_exclusive_group(required=True)
    scope_group.add_argument(
        "--all",
        action="store_true",
        help="Validate all detection rules under rules/detections",
    )
    scope_group.add_argument(
        "--since",
        help="Validate rules with base metadata date/modified >= dd/mm/yyyy",
    )

    return parser


def format_command_result(result: object) -> str:
    """Render CLI command results for stdout.

    Structured validator payloads are emitted as pretty JSON so operators can
    redirect the output into files and review or parse it consistently.
    """
    if isinstance(result, (dict, list)):
        return json.dumps(result, indent=2, ensure_ascii=False)
    return str(result)


def run_cli(
    build_app_fn: Callable[[], tuple[object, object, object, object, object]],
    argv: list[str] | None = None,
) -> None:
    """Parse args and execute the selected use case."""
    parser = create_parser()
    args = parser.parse_args(argv)

    load_tenant_uc, export_rules_uc, deploy_rules_uc, validate_tenant_uc, validate_rules_uc = (
        build_app_fn()
    )

    if args.command == "load-tenant":
        print(format_command_result(load_tenant_uc.execute(args.tenant_id)))
        return

    if args.command in {"gen-artifact", "export-rules"}:
        print(format_command_result(export_rules_uc.execute(args.tenant_id)))
        return

    if args.command == "validate-tenant":
        print(format_command_result(validate_tenant_uc.execute(args.tenant_id)))
        return

    if args.command == "validate-rules":
        print(format_command_result(validate_rules_uc.execute(since=args.since, validate_all=args.all)))
        return

    exported, _ = export_rules_uc.prepare_export(args.tenant_id)
    print(format_command_result(deploy_rules_uc.execute(args.tenant_id, exported)))


if __name__ == "__main__":
    raise SystemExit("Run `python main.py -h` from project root.")
