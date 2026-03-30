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
        rules_by_name = self._index_rules_by_name(rules)
        exported: list[dict] = []

        for rule in rules:
            raw = rule.raw or {}
            rule_type = self._normalize_rule_type(raw.get("rule_type"))
            if rule_type == "base":
                continue

            logsource = raw.get("logsource") or {}
            if rule_type == "analyst":
                logsource = self._derive_analyst_logsource(raw, rules_by_name, logsource)

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

    def _index_rules_by_name(self, rules: list[Rule]) -> dict[str, Rule]:
        """Index source rules by semantic `name` so analyst rules can resolve bases."""
        indexed: dict[str, Rule] = {}
        for rule in rules:
            rule_name = (rule.raw or {}).get("name")
            if isinstance(rule_name, str) and rule_name.strip():
                indexed[rule_name.strip()] = rule
        return indexed

    def _derive_analyst_logsource(
        self,
        raw_rule: dict,
        rules_by_name: dict[str, Rule],
        current_logsource: dict,
    ) -> dict:
        """Derive analyst logsource scope from referenced source rules when missing.

        Parameters:
            raw_rule: Analyst rule document being flattened.
            rules_by_name: Source rules keyed by semantic `name`.
            current_logsource: Any explicit logsource already present on the analyst rule.

        Returns:
            A logsource dict that prefers the analyst's own explicit values and falls
            back to the shared scope of its referenced detection/base rules.
        """
        derived = dict(current_logsource or {})
        references = ((raw_rule.get("correlation") or {}).get("rules")) or []
        referenced_logsources: list[dict] = []

        for reference in references:
            if not isinstance(reference, str):
                continue
            source_rule = rules_by_name.get(reference.strip())
            if source_rule is None:
                continue
            logsource = (source_rule.raw or {}).get("logsource") or {}
            if isinstance(logsource, dict) and logsource:
                referenced_logsources.append(logsource)

        for key in ("category", "product", "service"):
            if derived.get(key):
                continue
            values = {
                value.strip()
                for logsource in referenced_logsources
                for value in [logsource.get(key)]
                if isinstance(value, str) and value.strip()
            }
            if len(values) == 1:
                derived[key] = next(iter(values))

        return derived

    def _normalize_rule_type(self, value: object) -> str:
        """Normalize source rule types to the render pipeline vocabulary."""
        if not isinstance(value, str):
            return ""
        normalized = value.strip().lower()
        if normalized in {"base", "detection_base"}:
            return "base"
        return normalized
