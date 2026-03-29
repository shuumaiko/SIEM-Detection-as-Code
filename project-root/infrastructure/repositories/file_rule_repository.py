import shutil
from pathlib import Path

import yaml

from domain.models.rule import Rule
from domain.models.tenant import Tenant
from domain.repositories.rule_repository import RuleRepository
from infrastructure.file_loader.yaml_loader import YamlLoader


class _ArtifactYamlDumper(yaml.SafeDumper):
    """YAML dumper that renders selected multiline strings in block style."""


class _LiteralString(str):
    """Marker type for strings that should be serialized with YAML block style."""


def _represent_literal_string(dumper: yaml.SafeDumper, value: _LiteralString) -> yaml.ScalarNode:
    """Serialize marked multiline strings with `|` style so artifact queries stay readable.

    Parameters:
        dumper: Active YAML dumper instance.
        value: Marked multiline string value being serialized.

    Returns:
        A YAML scalar node forced to YAML literal block style.
    """
    return dumper.represent_scalar("tag:yaml.org,2002:str", str(value), style="|")


_ArtifactYamlDumper.add_representer(_LiteralString, _represent_literal_string)


class FileRuleRepository(RuleRepository):
    """File-backed rule repository implementation."""

    def __init__(self, base_path: str | Path, tenant_rules_path: str | Path) -> None:
        """Store base-rule root and artifact root used by the render pipeline."""
        self.base_path = Path(base_path)
        self.tenant_rules_path = Path(tenant_rules_path)
        self.loader = YamlLoader()

    def list_by_category(self, category: str) -> list[Rule]:
        """Read base rules from one category under the active rules root."""
        category_path = self._resolve_rules_root() / category
        return self._scan_base_rules(category_path)

    def list_for_tenant(self, tenant: Tenant, include_all: bool = False) -> list[Rule]:
        """Read exported tenant rule artifacts from the artifact layer.

        Parameters:
            tenant: Tenant whose rendered artifacts should be loaded.
            include_all: When True, return all saved artifacts even if disabled in
                the tenant deployment manifest.

        Returns:
            Lightweight `Rule` models rebuilt from persisted tenant artifacts so
            deployment flows can read the final SIEM query and resolved targets.
        """
        tenant_root = self._resolve_tenant_rules_root(tenant.tenant_id)
        if tenant_root is None:
            return []

        enabled_rule_ids = tenant.enabled_rule_ids()
        result: list[Rule] = []
        for path in sorted(list(tenant_root.rglob("*.yml")) + list(tenant_root.rglob("*.yaml"))):
            try:
                data = self.loader.load(path)
            except Exception:
                continue
            if not isinstance(data, dict):
                continue

            source_rule = data.get("source_rule") or {}
            if not isinstance(source_rule, dict):
                source_rule = {}

            rule_id = data.get("id") or source_rule.get("rule_id") or path.stem
            if not include_all and enabled_rule_ids and rule_id not in enabled_rule_ids:
                continue

            siem_ext = data.get("x_splunk_es", {}) if tenant.siem_id == "splunk" else {}
            result.append(
                Rule(
                    rule_id=rule_id,
                    category=data.get("category", "unknown"),
                    product=data.get("product"),
                    siem_query=siem_ext.get("search_query"),
                    siem_targets=siem_ext.get("targets"),
                    source_path=str(path.relative_to(tenant_root)),
                    raw=data,
                )
            )
        return result

    def list_render_candidates(self, tenant: Tenant) -> list[Rule]:
        """Read source rules that expose a hardcoded query for the tenant SIEM.

        Only `stable` rules are exported into the render pipeline. Transitional rules
        with statuses such as `test` remain in the source repository but are not
        rendered for deployment. Both `rules/detections/` and `rules/analysts/`
        are scanned so analyst correlation content can be rendered, while base
        rules remain available as semantic references for analyst resolution.
        """
        result: list[Rule] = []
        for rules_root in self._resolve_render_roots():
            for path in sorted(list(rules_root.rglob("*.yml")) + list(rules_root.rglob("*.yaml"))):
                try:
                    data = self.loader.load(path)
                except Exception:
                    continue
                if not isinstance(data, dict):
                    continue
                if self._normalize_status(data.get("status")) != "stable":
                    continue

                siem_query, siem_targets = self._extract_siem_config(data, tenant.siem_id or "")
                if not siem_query:
                    continue

                logsource = data.get("logsource", {})
                result.append(
                    Rule(
                        rule_id=data.get("id", path.stem),
                        category=logsource.get("category", data.get("category", "unknown")),
                        product=logsource.get("product", data.get("product")),
                        siem_query=siem_query,
                        siem_targets=siem_targets,
                        source_path=str(path.relative_to(self.base_path)),
                        raw=data,
                    )
                )
        return result

    def save_rendered_for_tenant(self, tenant_id: str, rendered_rules: list[dict]) -> None:
        """Write rendered tenant rule artifacts under `artifacts/<tenant>/tenant-rules/`.

        Parameters:
            tenant_id: Tenant whose artifact tree should be refreshed.
            rendered_rules: Artifact documents with rule-relative paths that mirror
                the source `rules/` tree.

        Side effects:
            Removes the previous tenant `tenant-rules/` directory before writing the
            new artifact set. Any stale summary-only artifact from the reverted
            export experiment is also removed so the artifact layer returns to the
            per-rule layout.
        """
        target_root = self.tenant_rules_path / tenant_id / "tenant-rules"
        if target_root.exists():
            shutil.rmtree(target_root)
        legacy_summary_path = self.tenant_rules_path / tenant_id / "export-summary.yml"
        if legacy_summary_path.exists():
            legacy_summary_path.unlink()

        for item in rendered_rules:
            relative_path = Path(str(item.get("relative_path") or ""))
            if relative_path.is_absolute() or ".." in relative_path.parts:
                continue

            document = item.get("document")
            if not isinstance(document, dict):
                continue

            output_path = target_root / relative_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as file:
                yaml.dump(
                    self._prepare_for_dump(document),
                    file,
                    Dumper=_ArtifactYamlDumper,
                    sort_keys=False,
                    allow_unicode=True,
                    width=4096,
                )

    def sync_artifact_enabled_states(self, tenant: Tenant) -> None:
        """Rewrite saved tenant artifacts so `targets.enabled` matches deployments.

        Parameters:
            tenant: Tenant freshly reloaded after `rule-deployments.yaml` was saved.

        Side effects:
            Reads persisted artifact files under `artifacts/<tenant>/tenant-rules/` and
            updates the SIEM-specific `targets.enabled` flag for every artifact whose
            `id` or `source_rule.rule_id` resolves to one deployment entry.
        """
        tenant_root = self._resolve_tenant_rules_root(tenant.tenant_id)
        if tenant_root is None:
            return

        enabled_by_rule_id = {
            item.rule_id: item.enabled for item in (tenant.rule_deployments or []) if item.rule_id
        }
        if not enabled_by_rule_id:
            return

        extension_key = self._resolve_siem_extension_key(tenant.siem_id or "")
        for path in sorted(list(tenant_root.rglob("*.yml")) + list(tenant_root.rglob("*.yaml"))):
            try:
                data = self.loader.load(path)
            except Exception:
                continue
            if not isinstance(data, dict):
                continue

            source_rule = data.get("source_rule") or {}
            if not isinstance(source_rule, dict):
                source_rule = {}

            rule_id = data.get("id") or source_rule.get("rule_id") or path.stem
            if rule_id not in enabled_by_rule_id:
                continue

            extension = data.get(extension_key)
            if not isinstance(extension, dict):
                continue

            targets = extension.get("targets") or {}
            if not isinstance(targets, dict):
                targets = {}

            # Deployment manifest is the final tenant decision, so it overrides
            # any enabled value coming from execution defaults or rule overrides.
            targets["enabled"] = enabled_by_rule_id[rule_id]
            extension["targets"] = targets
            data[extension_key] = extension

            with open(path, "w", encoding="utf-8") as file:
                yaml.dump(
                    self._prepare_for_dump(data),
                    file,
                    Dumper=_ArtifactYamlDumper,
                    sort_keys=False,
                    allow_unicode=True,
                    width=4096,
                )

    def _resolve_rules_root(self) -> Path:
        """Return the active detection rules root while supporting old folder names."""
        candidates = (
            self.base_path / "detections",
            self.base_path / "detection",
        )
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return candidates[0]

    def _resolve_tenant_rules_root(self, tenant_id: str) -> Path | None:
        """Return the tenant artifact root while supporting legacy artifact layouts."""
        candidates = (
            self.tenant_rules_path / tenant_id / "tenant-rules",
            self.tenant_rules_path / tenant_id / "tenant-rules" / "detections",
            self.tenant_rules_path / tenant_id / "tenant-rules" / "detection-raw",
            self.tenant_rules_path / tenant_id,
        )
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return None

    def _resolve_render_roots(self) -> tuple[Path, ...]:
        """Return source rule roots that participate in the hardcoded render flow."""
        roots: list[Path] = []
        for candidate in (self.base_path / "detections", self.base_path / "analysts"):
            if candidate.exists():
                roots.append(candidate)
        return tuple(roots)

    def _scan_base_rules(self, root: Path) -> list[Rule]:
        if not root.exists():
            return []

        result: list[Rule] = []
        for path in sorted(list(root.rglob("*.yml")) + list(root.rglob("*.yaml"))):
            try:
                data = self.loader.load(path)
            except Exception:
                continue
            if not isinstance(data, dict):
                continue
            result.append(
                Rule(
                    rule_id=data.get("id", path.stem),
                    category=data.get("category", "unknown"),
                    product=data.get("product"),
                    raw=data,
                )
            )
        return result

    def _extract_siem_config(self, data: dict, siem_id: str) -> tuple[str | None, dict]:
        """Extract the source hardcoded query and any pre-existing SIEM targets."""
        x_query = data.get("x_query") or {}
        if isinstance(x_query, dict):
            query = x_query.get(siem_id)
            if isinstance(query, str) and query.strip():
                return query, {}

        if siem_id == "splunk":
            x_splunk_es = data.get("x_splunk_es") or {}
            if isinstance(x_splunk_es, dict):
                query = x_splunk_es.get("search_query")
                if isinstance(query, str) and query.strip():
                    targets = x_splunk_es.get("targets") or {}
                    return query, targets if isinstance(targets, dict) else {}

        return None, {}

    def _normalize_status(self, value: object) -> str:
        """Normalize rule status comparisons for export filtering."""
        if not isinstance(value, str):
            return ""
        return value.strip().lower()

    def _prepare_for_dump(self, value: object) -> object:
        """Recursively mark multiline strings so artifact YAML stays human-readable.

        Parameters:
            value: Arbitrary document value before YAML serialization.

        Returns:
            The same logical document, but with multiline strings wrapped in a marker
            type that the artifact dumper serializes using block style.
        """
        if isinstance(value, dict):
            return {key: self._prepare_for_dump(item) for key, item in value.items()}
        if isinstance(value, list):
            return [self._prepare_for_dump(item) for item in value]
        if isinstance(value, set):
            return [self._prepare_for_dump(item) for item in sorted(value)]
        if isinstance(value, str) and "\n" in value:
            return _LiteralString(value)
        return value

    def _resolve_siem_extension_key(self, siem_id: str) -> str:
        """Return the artifact extension key used for one tenant SIEM."""
        if siem_id == "splunk":
            return "x_splunk_es"
        return f"x_{siem_id}"
