from __future__ import annotations

from pathlib import Path

from infrastructure.file_loader.yaml_loader import YamlLoader


class DetectionFieldMappingLoader:
    """Resolve source-rule fields to canonical fields from `mappings/detections/`.

    The loader reads shared detection field dictionaries once and selects the
    best matching document for one rule using the rule logsource metadata with a
    path-specificity tiebreaker.
    """

    _WILDCARD_VALUES = {"", "any", "generic", "unknown"}

    def __init__(self, mappings_root: str | Path) -> None:
        """Store the detection-mapping root used by the render pipeline."""
        self.mappings_root = Path(mappings_root)
        self.yaml_loader = YamlLoader()
        self._documents_cache: list[dict] | None = None

    def resolve_source_to_canonical_fields(
        self,
        *,
        category: object,
        product: object,
        service: object,
        source_path: object = None,
    ) -> dict[str, str]:
        """Return the best source-field to canonical-field dictionary for one rule.

        Parameters:
            category: Rule logsource category used for mapping selection.
            product: Rule logsource product used for mapping selection.
            service: Rule logsource service used for mapping selection.
            source_path: Optional source rule path under `rules/`, used only as a
                tiebreaker when multiple mapping documents share the same
                logsource specificity.

        Returns:
            A lowercase source-field alias map keyed by source field name and
            valued by canonical field name. Returns an empty dictionary when no
            compatible detection field dictionary can be resolved.
        """
        document = self._select_best_document(
            category=category,
            product=product,
            service=service,
            source_path=source_path,
        )
        if document is None:
            return {}

        resolved: dict[str, str] = {}
        for field_entry in document.get("fields") or []:
            if not isinstance(field_entry, dict):
                continue
            canonical_field = field_entry.get("canonical_field") or field_entry.get("target_field")
            if not isinstance(canonical_field, str) or not canonical_field.strip():
                continue
            for source_field in field_entry.get("source_fields") or []:
                if not isinstance(source_field, str) or not source_field.strip():
                    continue
                resolved[source_field.strip().lower()] = canonical_field.strip()
        return resolved

    def _select_best_document(
        self,
        *,
        category: object,
        product: object,
        service: object,
        source_path: object,
    ) -> dict | None:
        """Return the most specific detection mapping document for one rule."""
        request_logsource = (
            self._normalize_value(category),
            self._normalize_value(product),
            self._normalize_value(service),
        )
        request_path_parts = self._normalize_source_path(source_path)

        best_document: dict | None = None
        best_score: tuple[int, int, int, int] | None = None

        for document in self._load_documents():
            candidate_logsource = document.get("logsource") or {}
            if not isinstance(candidate_logsource, dict):
                continue

            match_score = self._score_logsource_match(candidate_logsource, request_logsource)
            if match_score is None:
                continue

            candidate_path_parts = tuple(document.get("_relative_dir_parts") or ())
            common_prefix_length = self._common_prefix_length(request_path_parts, candidate_path_parts)
            candidate_depth = len(candidate_path_parts)
            score = (
                match_score[0],
                match_score[1],
                common_prefix_length,
                candidate_depth,
            )
            if best_score is None or score > best_score:
                best_document = document
                best_score = score

        return best_document

    def _score_logsource_match(
        self,
        candidate_logsource: dict,
        request_logsource: tuple[str, str, str],
    ) -> tuple[int, int] | None:
        """Return a specificity score for one mapping document or `None` if incompatible."""
        exact_matches = 0
        wildcard_matches = 0

        for key, request_value in zip(("category", "product", "service"), request_logsource):
            candidate_value = self._normalize_value(candidate_logsource.get(key))
            if candidate_value in self._WILDCARD_VALUES or request_value in self._WILDCARD_VALUES:
                wildcard_matches += 1
                continue
            if candidate_value != request_value:
                return None
            exact_matches += 1

        return exact_matches, -wildcard_matches

    def _load_documents(self) -> list[dict]:
        """Load detection field dictionaries once from disk."""
        if self._documents_cache is not None:
            return self._documents_cache

        documents: list[dict] = []
        if not self.mappings_root.exists():
            self._documents_cache = documents
            return documents

        for path in sorted(
            list(self.mappings_root.rglob("*.yml")) + list(self.mappings_root.rglob("*.yaml"))
        ):
            try:
                data = self.yaml_loader.load(path)
            except Exception:
                continue
            if not isinstance(data, dict):
                continue
            if data.get("mapping_type") != "detection_fields":
                continue

            document = dict(data)
            document["_relative_dir_parts"] = path.relative_to(self.mappings_root).parent.parts
            documents.append(document)

        self._documents_cache = documents
        return documents

    def _normalize_source_path(self, source_path: object) -> tuple[str, ...]:
        """Normalize one `rules/` source path so it can be compared to mapping paths."""
        if not isinstance(source_path, str) or not source_path.strip():
            return ()

        parts = list(Path(source_path).parts)
        if parts and parts[0] in {"detections", "analysts"}:
            parts = parts[1:]
        if parts:
            parts = parts[:-1]
        return tuple(self._normalize_value(part) for part in parts if self._normalize_value(part))

    def _common_prefix_length(
        self,
        left_parts: tuple[str, ...],
        right_parts: tuple[str, ...],
    ) -> int:
        """Return the number of shared leading path segments between two paths."""
        common = 0
        for left_part, right_part in zip(left_parts, right_parts):
            if left_part != right_part:
                break
            common += 1
        return common

    def _normalize_value(self, value: object) -> str:
        """Normalize mapping comparisons so taxonomy matching stays predictable."""
        if not isinstance(value, str):
            return ""
        return value.strip().lower().replace("-", "").replace("_", "").replace(" ", "")
