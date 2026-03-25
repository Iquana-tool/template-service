import logging
from typing import Any

from mlflow import MlflowClient
from mlflow.exceptions import MlflowException
from mlflow.exceptions import RestException

logger = logging.getLogger(__name__)


def _registered_model_exists(client: MlflowClient, model_name: str) -> bool:
    try:
        client.get_registered_model(model_name)
        return True
    except (RestException, MlflowException):
        return False


def ensure_required_registry_models(
    tracking_uri: str,
    required_models: dict[str, list[str]],
    create_missing: bool = False,
) -> dict[str, Any]:
    """Check required MLflow registered-model entries and optionally create placeholders.

    This function intentionally creates only the registered-model records (no versions/artifacts),
    so services can enforce expected model names in template deployments.
    """
    client = MlflowClient(tracking_uri=tracking_uri)
    existing: list[str] = []
    missing: list[str] = []
    created: list[str] = []

    for capability, names in required_models.items():
        for base_name in names:
            model_name = f"{capability}.{base_name}"
            if _registered_model_exists(client, model_name):
                existing.append(model_name)
                continue

            if not create_missing:
                missing.append(model_name)
                continue

            client.create_registered_model(model_name)
            client.set_registered_model_tag(model_name, "is_placeholder", "true")
            client.set_registered_model_tag(model_name, "template_capability", capability)
            client.set_registered_model_tag(model_name, "template_base_name", base_name)
            created.append(model_name)
            logger.info("Created placeholder MLflow registered model '%s'", model_name)

    return {
        "tracking_uri": tracking_uri,
        "existing": existing,
        "missing": missing,
        "created": created,
    }


