from domain.models.rule import Rule
from domain.models.tenant import Tenant


class ExportService:
    """Serialize source rules into the flat payload used by the render pipeline."""

    def export_rules(self, tenant: Tenant, rules: list[Rule]) -> list[dict]:
        """Return renderable rule payloads enriched with logsource context.

        Parameters:
            tenant: Active tenant used for the render request.
            rules: Source rules already filtered to the current SIEM hardcoded-query path.

        Returns:
            A flat payload per renderable rule. `base` rules are kept available as
            semantic references for analyst correlation, but are not emitted as
            standalone deployable payloads.
        """
        exported: list[dict] = []

        for rule in rules:
            raw = rule.raw or {}
            rule_type = self._normalize_rule_type(raw.get("rule_type"))
            if rule_type == "base":
                continue

            logsource = self._resolve_rule_logsource(rule, raw, rule_type)
            if logsource is None:
                continue

            exported.append(
                {
                    "tenant_id": tenant.tenant_id,
                    "siem_id": tenant.siem_id,
                    "id": rule.rule_id,
                    "rule_type": rule_type or "detection",
                    "source_rule_name": raw.get("name"),
                    "source_path": rule.source_path,
                    "display_name": raw.get("title", rule.rule_id),
                    "category": logsource.get("category", rule.category),
                    "product": logsource.get("product", rule.product),
                    "service": logsource.get("service"),
                    "fields": raw.get("fields") or [],
                    "search_query": rule.siem_query,
                    "targets": rule.siem_targets or {},
                }
            )

        return exported

    def _resolve_rule_logsource(self, rule: Rule, raw_rule: dict, rule_type: str) -> dict | None:
        """Return the deploy scope for one rule or `None` when the rule must be skipped.

        Parameters:
            rule: Source rule model being flattened for the render pipeline.
            raw_rule: Original YAML document backing the source rule.
            rule_type: Normalized rule type such as `detection` or `analyst`.

        Returns:
            A shallow logsource dict used for tenant target resolution, or `None`
            when the rule is not deployable in the current hardcoded-query flow.

        Side effects:
            None. The returned dict is detached from the source YAML object.
        """
        raw_logsource = raw_rule.get("logsource") or {}
        logsource = dict(raw_logsource) if isinstance(raw_logsource, dict) else {}

        # Hardcoded-query is now execution-only for analyst content. Analyst rules
        # must carry their own deploy scope instead of inheriting it at runtime.
        if rule_type == "analyst" and not self._has_complete_logsource(logsource):
            return None

        if "category" not in logsource and isinstance(rule.category, str) and rule.category:
            logsource["category"] = rule.category
        if "product" not in logsource and isinstance(rule.product, str) and rule.product:
            logsource["product"] = rule.product
        return logsource

    def _has_complete_logsource(self, logsource: dict) -> bool:
        """Return True when one logsource dict declares the full deploy scope."""
        return all(
            isinstance(logsource.get(key), str) and logsource.get(key).strip()
            for key in ("category", "product", "service")
        )

    def _normalize_rule_type(self, value: object) -> str:
        """Normalize source rule types to the render pipeline vocabulary."""
        if not isinstance(value, str):
            return ""
        normalized = value.strip().lower()
        if normalized in {"base", "detection_base"}:
            return "base"
        return normalized
