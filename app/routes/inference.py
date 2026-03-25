from fastapi import APIRouter, Depends
from app.dependencies import get_current_backend
from app.state import Backend
from iquana_toolbox.schemas.networking.http.services import BaseImageRequest


router = APIRouter()

@router.post("/inference")
async def inference(request: BaseImageRequest, backend: Backend = Depends(get_current_backend)):
    """ Load a model from mlflow registry and perform inference on the provided image. This is a placeholder implementation. The actual logic will depend on the model and inference requirements."""
    # Example: model = backend.model_registry.load_model(request.model_id)
    raise NotImplementedError("Inference endpoint not implemented yet")

