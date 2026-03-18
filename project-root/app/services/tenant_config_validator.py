from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class TenantConfigValidator:
    """Validate tenant configuration files and cross-file references."""

    def __init__(self, tenants_root: str | Path, schemas_root: str | Path) -> None:
        self.tenants_root = Path(tenants_root)
        self.schemas_root = Path(schemas_root)

    def validate(self, tenant_id: str) -> dict:
        errors: list[str] = []
        warnings: list[str] = []
        files_checked = 0

        tenant_dir = self.tenants_root / tenant_id
        if not tenant_dir.exists():
            return self._result(
                tenant_id=tenant_id,
                files_checked=0,
                errors=[f"Tenant directory not found: {tenant_dir}"],
                warnings=[],
            )

        validator = self._build_schema_validator()
        if validator is None:
            warnings.append("jsonschema is not installed; schema validation is skipped.")

        tenant_file = tenant_dir / "tenant.yaml"
        tenant_data = self._load_yaml(tenant_file, errors)
        if tenant_data is not None:
            files_checked += 1
            self._validate_schema("tenant.schema.json", tenant_file, tenant_data, validator, errors)

        tenant_siem_id = (tenant_data or {}).get("siem_id")
        tenant_id_in_config = (tenant_data or {}).get("tenant_id")
        if tenant_id_in_config and tenant_id_in_config != tenant_id:
            errors.append(
                f"{tenant_file}: tenant_id mismatch (expected '{tenant_id}', got '{tenant_id_in_config}')."
            )

        device_files = sorted((tenant_dir / "devices").glob("*.yaml"))
        logsource_files = sorted((tenant_dir / "logsources").glob("*.yaml"))
        bindings_dir = tenant_dir / "bindings"
        ingest_binding_files = (
            sorted((bindings_dir / "ingest").glob("*.yaml"))
            if (bindings_dir / "ingest").exists()
            else sorted(bindings_dir.glob("*.yaml"))
        )
        field_binding_files = sorted((bindings_dir / "fields").glob("*.yaml"))
        rules_file = self._resolve_rule_deployment_file(tenant_dir, warnings)

        if not device_files:
            warnings.append(f"No device files found in {(tenant_dir / 'devices')}.")
        if not logsource_files:
            warnings.append(f"No logsource files found in {(tenant_dir / 'logsources')}.")
        if not ingest_binding_files:
            warnings.append(f"No binding files found in {(tenant_dir / 'bindings')}.")
        if rules_file is None:
            warnings.append(
                f"No rule deployment file found in {tenant_dir} "
                "(expected deployments/rule-deployments.yaml)."
            )

        device_by_id: dict[str, dict[str, Any]] = {}
        logsource_datasets_by_device: dict[str, set[str]] = {}
        binding_datasets_by_device: dict[str, set[str]] = {}

        for file_path in device_files:
            data = self._load_yaml(file_path, errors)
            if data is None:
                continue
            files_checked += 1
            self._validate_schema("device.schema.json", file_path, data, validator, errors)
            self._validate_tenant_id(file_path, data.get("tenant_id"), tenant_id, errors)

            device_id = data.get("device_id")
            if not device_id:
                errors.append(f"{file_path}: missing required field 'device_id'.")
                continue
            if device_id in device_by_id:
                errors.append(f"{file_path}: duplicate device_id '{device_id}'.")
                continue
            device_by_id[device_id] = data

        for file_path in logsource_files:
            data = self._load_yaml(file_path, errors)
            if data is None:
                continue
            files_checked += 1
            self._validate_schema("logsource.schema.json", file_path, data, validator, errors)

            device_id = data.get("device_id")
            if not device_id:
                errors.append(f"{file_path}: missing required field 'device_id'.")
                continue
            if device_id not in device_by_id:
                errors.append(f"{file_path}: unknown device_id '{device_id}' (not found in devices/*).")

            datasets = data.get("datasets")
            if datasets is None:
                datasets = data.get("service") or []
            if not isinstance(datasets, list):
                errors.append(f"{file_path}: field 'datasets' must be an array.")
                continue

            dataset_ids: set[str] = set()
            for item in datasets:
                if not isinstance(item, dict):
                    errors.append(f"{file_path}: each item in 'datasets' must be an object.")
                    continue
                dataset_id = item.get("dataset_id") or item.get("service_id")
                if not dataset_id:
                    errors.append(f"{file_path}: dataset item missing 'dataset_id'.")
                    continue
                if dataset_id in dataset_ids:
                    errors.append(f"{file_path}: duplicate dataset_id '{dataset_id}'.")
                    continue
                dataset_ids.add(dataset_id)

            logsource_datasets_by_device[device_id] = dataset_ids

        for file_path in ingest_binding_files:
            data = self._load_yaml(file_path, errors)
            if data is None:
                continue
            files_checked += 1
            self._validate_schema("binding.schema.json", file_path, data, validator, errors)
            self._validate_tenant_id(file_path, data.get("tenant_id"), tenant_id, errors)

            device_id = data.get("device_id")
            if not device_id:
                errors.append(f"{file_path}: missing required field 'device_id'.")
                continue
            if device_id not in device_by_id:
                errors.append(f"{file_path}: unknown device_id '{device_id}' (not found in devices/*).")

            binding_siem_id = data.get("siem_id")
            if tenant_siem_id and binding_siem_id and binding_siem_id != tenant_siem_id:
                errors.append(
                    f"{file_path}: siem_id mismatch "
                    f"(tenant '{tenant_siem_id}', binding '{binding_siem_id}')."
                )

            datasets = data.get("datasets")
            if datasets is not None:
                if not isinstance(datasets, list):
                    errors.append(f"{file_path}: field 'datasets' must be an array.")
                    continue
                dataset_ids: set[str] = set()
                for item in datasets:
                    if not isinstance(item, dict):
                        errors.append(f"{file_path}: each item in 'datasets' must be an object.")
                        continue
                    dataset_id = item.get("dataset_id")
                    if not dataset_id:
                        errors.append(f"{file_path}: dataset item missing 'dataset_id'.")
                        continue
                    if dataset_id in dataset_ids:
                        errors.append(f"{file_path}: duplicate dataset_id '{dataset_id}'.")
                        continue
                    dataset_ids.add(dataset_id)
                binding_datasets_by_device[device_id] = dataset_ids
                continue

            bindings = data.get("bindings") or {}
            if not isinstance(bindings, dict):
                errors.append(f"{file_path}: field 'bindings' must be an object.")
                continue
            binding_datasets_by_device[device_id] = set(bindings.keys())

        for file_path in field_binding_files:
            data = self._load_yaml(file_path, errors)
            if data is None:
                continue
            files_checked += 1
            self._validate_tenant_id(file_path, data.get("tenant_id"), tenant_id, errors)

            device_id = data.get("device_id")
            if not device_id:
                errors.append(f"{file_path}: missing required field 'device_id'.")
                continue
            if device_id not in device_by_id:
                errors.append(f"{file_path}: unknown device_id '{device_id}' (not found in devices/*).")

            binding_siem_id = data.get("siem_id")
            if tenant_siem_id and binding_siem_id and binding_siem_id != tenant_siem_id:
                errors.append(
                    f"{file_path}: siem_id mismatch "
                    f"(tenant '{tenant_siem_id}', binding '{binding_siem_id}')."
                )

            field_mapping = data.get("field_mapping")
            if field_mapping is None:
                errors.append(f"{file_path}: missing required field 'field_mapping'.")
                continue
            if not isinstance(field_mapping, dict):
                errors.append(f"{file_path}: field 'field_mapping' must be an object.")

        for device_id in sorted(set(logsource_datasets_by_device) | set(binding_datasets_by_device)):
            log_datasets = logsource_datasets_by_device.get(device_id, set())
            bind_datasets = binding_datasets_by_device.get(device_id, set())

            missing = sorted(log_datasets - bind_datasets)
            extra = sorted(bind_datasets - log_datasets)
            if missing:
                errors.append(
                    f"device_id '{device_id}': missing bindings for dataset_id(s): {', '.join(missing)}."
                )
            if extra:
                errors.append(
                    f"device_id '{device_id}': bindings refer unknown dataset_id(s): {', '.join(extra)}."
                )

        if rules_file is not None:
            rules_data = self._load_yaml(rules_file, errors)
            if rules_data is not None:
                files_checked += 1
                self._validate_schema(
                    "rule_deployments.schema.json",
                    rules_file,
                    rules_data,
                    validator,
                    errors,
                )
                self._validate_tenant_id(rules_file, rules_data.get("tenant_id"), tenant_id, errors)
                deployments = rules_data.get("rule_deployments_by_siem") or {}
                if tenant_siem_id and tenant_siem_id not in deployments:
                    warnings.append(
                        f"{rules_file}: tenant siem_id '{tenant_siem_id}' "
                        "does not exist under rule_deployments_by_siem."
                    )

        return self._result(
            tenant_id=tenant_id,
            files_checked=files_checked,
            errors=errors,
            warnings=warnings,
        )

    def _result(
        self,
        tenant_id: str,
        files_checked: int,
        errors: list[str],
        warnings: list[str],
    ) -> dict:
        return {
            "tenant_id": tenant_id,
            "valid": len(errors) == 0,
            "summary": {
                "files_checked": files_checked,
                "errors": len(errors),
                "warnings": len(warnings),
            },
            "errors": errors,
            "warnings": warnings,
        }

    def _resolve_rule_deployment_file(self, tenant_dir: Path, warnings: list[str]) -> Path | None:
        candidates = (
            tenant_dir / "deployments" / "rule-deployments.yaml",
            tenant_dir / "rule-deployments.yaml",
        )
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return None

    def _build_schema_validator(self) -> Any | None:
        try:
            import jsonschema  # type: ignore
        except ModuleNotFoundError:
            return None
        return jsonschema

    def _validate_schema(
        self,
        schema_name: str,
        file_path: Path,
        data: dict,
        validator: Any | None,
        errors: list[str],
    ) -> None:
        if validator is None:
            return
        schema_path = self.schemas_root / schema_name
        if not schema_path.exists():
            errors.append(f"Schema not found: {schema_path}")
            return

        try:
            schema = self._load_json(schema_path)
            validator.validate(instance=data, schema=schema)
        except Exception as exc:
            errors.append(f"{file_path}: schema validation error: {exc}")

    def _validate_tenant_id(
        self,
        file_path: Path,
        actual_tenant_id: Any,
        expected_tenant_id: str,
        errors: list[str],
    ) -> None:
        if actual_tenant_id is None:
            errors.append(f"{file_path}: missing required field 'tenant_id'.")
            return
        if actual_tenant_id != expected_tenant_id:
            errors.append(
                f"{file_path}: tenant_id mismatch (expected '{expected_tenant_id}', got '{actual_tenant_id}')."
            )

    def _load_json(self, path: Path) -> dict:
        import json

        with open(path, "r", encoding="utf-8-sig") as file:
            return json.load(file)

    def _load_yaml(self, path: Path, errors: list[str]) -> dict | None:
        if not path.exists():
            errors.append(f"Missing file: {path}")
            return None
        try:
            with open(path, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file) or {}
            if not isinstance(data, dict):
                errors.append(f"{path}: YAML root must be an object.")
                return None
            return data
        except Exception as exc:
            errors.append(f"{path}: failed to parse YAML: {exc}")
            return None
