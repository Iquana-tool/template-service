from fastapi import APIRouter, HTTPException
from iquana_toolbox.schemas.networking.http.services import ServiceRegistrationRequest, ServiceRegistrationResponse
from app.mlflow_registry import ensure_required_registry_models
from app.state import (
    REGISTRY_CREATE_MISSING,
    REGISTRY_ENFORCE_REQUIRED,
    update_celery_config,
    verify_registration_token,
    register_backend,
)
from models import REQUIRED_BASE_MODELS
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/register", response_model=ServiceRegistrationResponse, tags=["admin"])
async def register_service(request: ServiceRegistrationRequest):
    """
    Register the service with the main backend.
    Receives configuration for Celery, MLFlow, and authentication.
    """
    try:
        # Verify registration token
        if not verify_registration_token(request.registration_token):
            raise HTTPException(status_code=401, detail="Invalid registration token")

        # Configure the global Celery app with the backend's broker so workers can connect.
        celery_result = update_celery_config(request.celery_broker_url)
        if not celery_result:
            raise HTTPException(status_code=400, detail="Failed to configure Celery")

        registry_result = ensure_required_registry_models(
            tracking_uri=request.mlflow_tracking_uri,
            required_models=REQUIRED_BASE_MODELS,
            create_missing=REGISTRY_CREATE_MISSING,
        )

        if registry_result["missing"] and REGISTRY_ENFORCE_REQUIRED:
            missing_str = ", ".join(registry_result["missing"])
            raise HTTPException(
                status_code=400,
                detail=(
                    "MLflow registry is missing required base models: "
                    f"{missing_str}. "
                    "Enable REGISTRY_CREATE_MISSING=true to auto-create placeholders."
                ),
            )

        backend_token = register_backend(
            backend_address=request.backend_url,
            celery_broker_url=request.celery_broker_url,
            mlflow_tracking_uri=request.mlflow_tracking_uri,
            api_key=request.api_key,
        )

        service_id = str(uuid.uuid4())
        logger.info(f"Service registered successfully with ID: {service_id}")
        logger.info(f"Celery broker: {request.celery_broker_url}")
        logger.info(f"MLFlow tracking URI: {request.mlflow_tracking_uri}")
        if registry_result["created"]:
            logger.info("Created placeholder registry models: %s", ", ".join(registry_result["created"]))
        if registry_result["existing"]:
            logger.info("Verified existing registry models: %s", ", ".join(registry_result["existing"]))
        logger.info("Issued backend token for backend: %s", request.backend_url)

        return ServiceRegistrationResponse(
            success=True,
            message=f"Service registered successfully. Use Authorization: Bearer {backend_token}",
            service_id=service_id
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")