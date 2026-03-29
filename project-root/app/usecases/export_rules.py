from app.services.export_service import ExportService
from app.services.rule_artifact_service import RuleArtifactService
from app.services.rule_deployment_builder import RuleDeploymentBuilder
from app.services.rule_service import RuleService
from domain.repositories.rule_repository import RuleRepository
from domain.repositories.tenant_repository import TenantRepository


class ExportRulesUseCase:
    """Generate tenant rule artifacts and return a compact export summary."""

    def __init__(
        self,
        tenant_repository: TenantRepository,
        rule_repository: RuleRepository,
        deployment_builder: RuleDeploymentBuilder,
        artifact_service: RuleArtifactService,
    ) -> None:
        """Store dependencies used by the hardcoded-query render pipeline."""
        self.tenant_repository = tenant_repository
        self.rule_service = RuleService(rule_repository)
        self.export_service = ExportService()
        self.deployment_builder = deployment_builder
        self.artifact_service = artifact_service

    def execute(self, tenant_id: str) -> dict:
        """Generate artifacts for one tenant and return CLI-friendly summary metadata."""
        _, summary = self.prepare_export(tenant_id)
        return summary

    def prepare_export(self, tenant_id: str) -> tuple[list[dict], dict]:
        """Prepare artifact generation data and persist per-rule tenant artifacts.

        Parameters:
            tenant_id: Tenant identifier whose artifacts should be regenerated.

        Returns:
            A tuple of `(mapped_rules, summary)` where `mapped_rules` keeps the
            deploy-ready internal payload and `summary` is the compact metadata
            returned to CLI and API callers.
        """
        tenant = self.tenant_repository.get_by_id(tenant_id)
        rules = self.rule_service.load_render_candidates(tenant)
        exported = self.export_service.export_rules(tenant, rules)
        mapped_rules, deployment_payload = self.deployment_builder.build(tenant, exported)
        artifact_rules = self.artifact_service.build_artifacts(tenant, rules, mapped_rules)
        self.rule_service.save_rendered_rules_for_tenant(tenant.tenant_id, artifact_rules)
        self.tenant_repository.save_rule_deployments(tenant_id, deployment_payload)
        refreshed_tenant = self.tenant_repository.get_by_id(tenant_id)
        self.rule_service.sync_artifact_enabled_states(refreshed_tenant)
        return mapped_rules, self._build_summary(tenant, mapped_rules)

    def _build_summary(self, tenant, mapped_rules: list[dict]) -> dict:
        """Build the compact metadata payload returned by CLI and API flows.

        Parameters:
            tenant: Active tenant used for scoping the summary result.
            mapped_rules: Final rendered rule payloads after ingest resolution.

        Returns:
            A small JSON-serializable summary that highlights how many rules were
            materialized and which tenant logsource targets they cover.
        """
        rule_count_by_type: dict[str, int] = {}
        device_ids: set[str] = set()
        dataset_ids: set[str] = set()
        logsources: dict[tuple[str, str, str], dict] = {}

        for item in mapped_rules:
            rule_type = str(item.get("rule_type") or "unknown")
            rule_count_by_type[rule_type] = rule_count_by_type.get(rule_type, 0) + 1

            key = (
                str(item.get("category") or "unknown"),
                str(item.get("product") or "unknown"),
                str(item.get("service") or "unknown"),
            )
            rollup = logsources.setdefault(
                key,
                {
                    "category": key[0],
                    "product": key[1],
                    "service": key[2],
                    "rule_count": 0,
                    "device_ids": set(),
                    "dataset_ids": set(),
                    "indexes": set(),
                    "sourcetypes": set(),
                },
            )
            rollup["rule_count"] += 1

            # Prefer the fully expanded ingest target list because one rule may map
            # to multiple tenant datasets.
            targets = item.get("targets") or {}
            ingest_targets = targets.get("ingest_targets")
            if not isinstance(ingest_targets, list):
                ingest_targets = [targets]

            for target in ingest_targets:
                if not isinstance(target, dict):
                    continue
                device_id = target.get("device_id")
                dataset_id = target.get("dataset_id")
                index = target.get("index")
                sourcetype = target.get("sourcetype")

                if isinstance(device_id, str) and device_id:
                    device_ids.add(device_id)
                    rollup["device_ids"].add(device_id)
                if isinstance(dataset_id, str) and dataset_id:
                    dataset_ids.add(dataset_id)
                    rollup["dataset_ids"].add(dataset_id)
                if isinstance(index, str) and index:
                    rollup["indexes"].add(index)
                if isinstance(sourcetype, str) and sourcetype:
                    rollup["sourcetypes"].add(sourcetype)

        deployed_logsources = []
        for key in sorted(logsources.keys()):
            rollup = dict(logsources[key])
            for field in ("device_ids", "dataset_ids", "indexes", "sourcetypes"):
                rollup[field] = sorted(rollup[field])
            deployed_logsources.append(rollup)

        return {
            "tenant_id": tenant.tenant_id,
            "siem_id": tenant.siem_id,
            "generated_artifact_count": len(mapped_rules),
            "rule_count_by_type": dict(sorted(rule_count_by_type.items())),
            "deployed_device_ids": sorted(device_ids),
            "deployed_dataset_ids": sorted(dataset_ids),
            "deployed_logsources": deployed_logsources,
            "artifact_root": f"artifacts/{tenant.tenant_id}/tenant-rules",
            "deployment_manifest_path": f"tenants/{tenant.tenant_id}/deployments/rule-deployments.yaml",
        }
