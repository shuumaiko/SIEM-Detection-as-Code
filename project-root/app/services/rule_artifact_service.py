from __future__ import annotations

from copy import deepcopy

from domain.models.rule import Rule
from domain.models.tenant import Tenant
from infrastructure.file_loader.execution_config_loader import ExecutionConfigLoader


class RuleArtifactService:
    """Build rendered tenant artifact documents from source rules and resolved queries."""

    def __init__(self, execution_loader: ExecutionConfigLoader) -> None:
        """Store execution loader used to enrich artifact metadata."""
        self.execution_loader = execution_loader

    def build_artifacts(
        self,
        tenant: Tenant,
        source_rules: list[Rule],
        resolved_rules: list[dict],
    ) -> list[dict]:
        """Return artifact documents ready to be persisted under `artifacts/<tenant>/tenant-rules`."""
        artifacts: list[dict] = []
        rules_by_id = {rule.rule_id: rule for rule in source_rules}

        for item in resolved_rules:
            source_rule = rules_by_id.get(item.get("id"))
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
                    "relative_path": source_rule.source_path,
                    "document": self._build_document(tenant, source_rule, item, execution),
                }
            )

        return artifacts

    def _build_document(
        self,
        tenant: Tenant,
        source_rule: Rule,
        resolved_rule: dict,
        execution: dict,
    ) -> dict:
        """Create the final artifact document for one rule render result."""
        document = deepcopy(source_rule.raw or {})
        display_name = (
            execution.get("display_name")
            or document.get("title")
            or resolved_rule.get("display_name")
            or source_rule.rule_id
        )

        # Keep the source `x_query` for traceability, but store the final deployable query separately.
        document["title"] = display_name
        document[self._siem_extension_key(tenant.siem_id or "")] = {
            "targets": self._build_targets_payload(resolved_rule.get("targets") or {}, execution),
            "search_query": resolved_rule.get("search_query"),
        }
        return document

    def _build_targets_payload(self, base_targets: dict, execution: dict) -> dict:
        """Merge resolved ingest targets with the effective execution metadata."""
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
