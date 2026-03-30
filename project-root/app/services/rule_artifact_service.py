from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

from domain.models.rule import Rule
from domain.models.tenant import Tenant
from infrastructure.file_loader.execution_config_loader import ExecutionConfigLoader


class RuleArtifactService:
    """Build deployable tenant rule artifacts from source rules and resolved targets."""

    def __init__(self, execution_loader: ExecutionConfigLoader) -> None:
        """Store execution loader used to enrich per-rule artifact metadata."""
        self.execution_loader = execution_loader

    def build_artifacts(
        self,
        tenant: Tenant,
        source_rules: list[Rule],
        resolved_rules: list[dict],
    ) -> list[dict]:
        """Return per-rule artifact documents ready for tenant-and-SIEM artifact storage.

        Parameters:
            tenant: Active tenant whose artifacts are being rendered.
            source_rules: Source rules that participated in the render flow.
            resolved_rules: Final rendered rule payloads after target resolution.

        Returns:
            One artifact entry per rendered deployable rule. Each entry keeps the
            original rule-relative path so the repository artifact tree mirrors
            the source `rules/` layout.
        """
        rules_by_id = {rule.rule_id: rule for rule in source_rules}
        artifacts: list[dict] = []

        for item in resolved_rules:
            source_rule_id = item.get("source_rule_id") or item.get("id")
            source_rule = rules_by_id.get(source_rule_id)
            if source_rule is None or not source_rule.source_path:
                continue

            execution = self.execution_loader.load_effective_config(
                tenant_id=tenant.tenant_id,
                siem_id=tenant.siem_id or "",
                rule_id=source_rule.rule_id,
                rule_name=(source_rule.raw or {}).get("name"),
                rule_level=(source_rule.raw or {}).get("level"),
            )
            artifacts.append(
                {
                    "relative_path": self._build_relative_artifact_path(
                        source_rule.source_path,
                        item.get("artifact_suffix"),
                    ),
                    "document": self._build_rule_artifact(
                        tenant=tenant,
                        source_rule=source_rule,
                        resolved_rule=item,
                        execution=execution,
                    ),
                }
            )

        return artifacts

    def _build_rule_artifact(
        self,
        tenant: Tenant,
        source_rule: Rule,
        resolved_rule: dict,
        execution: dict,
    ) -> dict:
        """Build one deployable tenant artifact in the repository envelope format.

        Parameters:
            tenant: Active tenant used for artifact scoping.
            source_rule: Original source rule document.
            resolved_rule: Deployable render payload after ingest target resolution.
            execution: Effective execution metadata merged from defaults and overrides.

        Returns:
            One tenant artifact document with the source metadata envelope plus
            the final SIEM-specific query and resolved targets.
        """
        document = deepcopy(source_rule.raw or {})
        rendered_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        display_name = (
            execution.get("display_name")
            or document.get("title")
            or resolved_rule.get("display_name")
            or source_rule.rule_id
        )
        prefixed_display_name = self._prefix_with_device_id(
            display_name,
            resolved_rule.get("targets") or {},
        )
        normalized_source_path = str(source_rule.source_path).replace("\\", "/")

        artifact = {
            "artifact_schema_version": 1.0,
            "artifact_type": "tenant_rule",
            "id": resolved_rule.get("id") or source_rule.rule_id,
            "tenant_id": tenant.tenant_id,
            "siem_id": tenant.siem_id,
            "source_rule": {
                "rule_id": source_rule.rule_id,
                "rule_name": document.get("name"),
                "rule_type": document.get("rule_type"),
                "source_path": f"rules/{normalized_source_path}",
                "status": document.get("status"),
                "level": document.get("level"),
                "version": document.get("version"),
            },
            "display_name": prefixed_display_name,
            "metadata": {
                "tags": document.get("tags") or [],
                "owner": document.get("author"),
                "last_rendered": rendered_at,
            },
            self._siem_extension_key(tenant.siem_id or ""): {
                "targets": self._build_targets_payload(resolved_rule.get("targets") or {}, execution),
                "search_query": resolved_rule.get("search_query"),
            },
        }
        return artifact

    def _build_relative_artifact_path(self, source_path: str, artifact_suffix: object) -> str:
        """Return the tenant artifact path, optionally suffixed per target variant.

        Parameters:
            source_path: Original relative path under `rules/`.
            artifact_suffix: Optional suffix such as `__device__dataset` used to
                distinguish multiple artifacts derived from one source rule.

        Returns:
            A relative artifact path that preserves the source folder layout while
            making split variants unique on disk.
        """
        normalized = Path(str(source_path))
        if not isinstance(artifact_suffix, str) or not artifact_suffix:
            return str(normalized)
        return str(normalized.with_name(f"{normalized.stem}{artifact_suffix}{normalized.suffix}"))

    def _build_targets_payload(self, base_targets: dict, execution: dict) -> dict:
        """Merge resolved ingest targets with the effective execution metadata.

        Parameters:
            base_targets: Ingest target payload after tenant mapping resolution.
            execution: Effective execution metadata for the rule.

        Returns:
            A target payload ready to be serialized into the SIEM-specific
            artifact extension.
        """
        targets = deepcopy(base_targets)
        schedule = execution.get("schedule") or {}
        notable = execution.get("notable") or {}

        if schedule.get("cron"):
            targets["schedule_cron"] = schedule["cron"]
        if schedule.get("earliest"):
            targets["earliest"] = schedule["earliest"]
        if schedule.get("latest"):
            targets["latest"] = schedule["latest"]
        if notable:
            targets["notable"] = notable
        if "enabled" in execution:
            targets["enabled"] = execution["enabled"]
        return targets

    def _siem_extension_key(self, siem_id: str) -> str:
        """Return the artifact key used to store final SIEM-specific query output."""
        if siem_id == "splunk":
            return "x_splunk_es"
        return f"x_{siem_id}"

    def _prefix_with_device_id(self, display_name: object, targets: dict) -> str:
        """Prefix one rendered rule title with its resolved device_id when unambiguous.

        Parameters:
            display_name: Current display title selected for the rendered rule.
            targets: Resolved target payload, which may include one direct device_id or
                an `ingest_targets` list built from tenant bindings.

        Returns:
            The original title, or `<device_id> - <title>` when exactly one device_id can
            be derived from the render targets.
        """
        base_name = str(display_name)
        device_id = self._resolve_single_device_id(targets)
        if not device_id:
            return base_name
        prefix = f"{device_id} - "
        if base_name.startswith(prefix):
            return base_name
        return f"{prefix}{base_name}"

    def _resolve_single_device_id(self, targets: dict) -> str | None:
        """Return one device_id when the render targets map to a single tenant device."""
        direct_device_id = targets.get("device_id")
        if isinstance(direct_device_id, str) and direct_device_id.strip():
            return direct_device_id.strip()

        ingest_targets = targets.get("ingest_targets")
        if not isinstance(ingest_targets, list):
            return None

        device_ids = {
            item.get("device_id").strip()
            for item in ingest_targets
            if isinstance(item, dict)
            and isinstance(item.get("device_id"), str)
            and item.get("device_id").strip()
        }
        if len(device_ids) == 1:
            return next(iter(device_ids))
        return None
