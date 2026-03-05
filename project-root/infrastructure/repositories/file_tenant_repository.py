from pathlib import Path

import yaml

from domain.models.binding import Binding
from domain.models.device import Device
from domain.models.logsource import LogSource
from domain.models.rule_deployment import RuleDeployment
from domain.models.tenant import Tenant
from domain.repositories.tenant_repository import TenantRepository
from infrastructure.file_loader.yaml_loader import YamlLoader


class FileTenantRepository(TenantRepository):
    """File-backed tenant repository implementation."""

    def __init__(self, base_path: str | Path) -> None:
        self.base_path = Path(base_path)
        self.loader = YamlLoader()

    def get_by_id(self, tenant_id: str) -> Tenant:
        tenant_file = self.base_path / tenant_id / "tenant.yaml"
        if not tenant_file.exists():
            return Tenant(tenant_id=tenant_id)

        tenant_data = self.loader.load(tenant_file)
        tenant_root = tenant_file.parent

        tenant = Tenant(
            tenant_id=tenant_data.get("tenant_id", tenant_id),
            siem_id=tenant_data.get("siem_id"),
        )
        tenant.devices = self._load_devices(tenant_root, tenant.tenant_id)
        tenant.logsources = self._load_logsources(tenant_root)
        tenant.bindings = self._load_bindings(tenant_root)
        tenant.rule_deployments = self._load_rule_deployments(tenant_root, tenant.siem_id)
        return tenant

    def _load_devices(self, tenant_root: Path, tenant_id: str) -> dict[str, Device]:
        result: dict[str, Device] = {}
        devices_root = tenant_root / "devices"
        for file_path in sorted(devices_root.glob("*.y*ml")):
            data = self.loader.load(file_path)
            device_id = data.get("device_id")
            if not device_id:
                continue
            result[device_id] = Device(
                tenant_id=data.get("tenant_id", tenant_id),
                device_id=device_id,
                device_type=data.get("device_type"),
                vendor=data.get("vendor"),
                product=data.get("product"),
            )
        return result

    def _load_logsources(self, tenant_root: Path) -> dict[str, LogSource]:
        result: dict[str, LogSource] = {}
        logsources_root = tenant_root / "logsources"
        if not logsources_root.exists():
            logsources_root = tenant_root / "logsource"

        for file_path in sorted(logsources_root.glob("*.y*ml")):
            data = self.loader.load(file_path)
            device_id = data.get("device_id")
            if not device_id:
                continue
            result[device_id] = LogSource(
                device_id=device_id,
                status="active",
                services=data.get("service", []),
            )
        return result

    def _load_bindings(self, tenant_root: Path) -> dict[str, Binding]:
        result: dict[str, Binding] = {}
        bindings_root = tenant_root / "bindings"
        for file_path in sorted(bindings_root.glob("*.y*ml")):
            data = self.loader.load(file_path)
            device_id = data.get("device_id")
            if not device_id:
                continue
            result[device_id] = Binding(
                tenant_id=data.get("tenant_id", ""),
                device_id=device_id,
                siem_id=data.get("siem_id", ""),
                bindings=data.get("bindings", {}),
            )
        return result

    def _load_rule_deployments(self, tenant_root: Path, siem_id: str | None) -> list[RuleDeployment]:
        deployment_file = self._resolve_rule_deployment_file(tenant_root)
        if deployment_file is None:
            return []

        data = self.loader.load(deployment_file)
        deployment_by_siem = data.get("rule_deployments_by_siem", {})
        if not isinstance(deployment_by_siem, dict):
            return []

        selected = deployment_by_siem.get(siem_id or "", [])
        if not isinstance(selected, list):
            return []

        result: list[RuleDeployment] = []
        for item in selected:
            if not isinstance(item, dict):
                continue
            rule_id = item.get("rule_id")
            if not rule_id:
                continue
            result.append(
                RuleDeployment(
                    rule_id=rule_id,
                    enabled=bool(item.get("enabled", True)),
                    display_name=item.get("display_name"),
                )
            )
        return result

    def _resolve_rule_deployment_file(self, tenant_root: Path) -> Path | None:
        canonical = tenant_root / "rule-deployments.yaml"
        if canonical.exists():
            return canonical
        return None

    def save_rule_deployments(self, tenant_id: str, payload: dict) -> None:
        tenant_root = self.base_path / tenant_id
        tenant_root.mkdir(parents=True, exist_ok=True)
        target_path = tenant_root / "rule-deployments.yaml"
        with open(target_path, "w", encoding="utf-8") as file:
            yaml.safe_dump(payload, file, sort_keys=False, allow_unicode=True)
