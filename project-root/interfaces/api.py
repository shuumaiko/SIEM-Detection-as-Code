"""
API skeleton. Replace with FastAPI/Flask wiring when needed.
"""

from main import build_app


def health() -> dict:
    """Simple health endpoint for API integration tests."""
    return {"status": "ok"}


def export_rules(tenant_id: str) -> dict:
    """Generate tenant artifacts and return compact summary metadata."""
    _, export_rules_uc, _, _, _ = build_app()
    return export_rules_uc.execute(tenant_id)
