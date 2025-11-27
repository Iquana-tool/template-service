from fastapi import status, HTTPException, Response

from app.schemas.inference import Request
from app.state import MODEL_CACHE, IMAGE_CACHE, MODEL_REGISTRY
from models.base_models import BaseModel
from fastapi import APIRouter


router = APIRouter()
session_router = APIRouter(prefix="/annotation_session", tags=["annotation_session"])

@session_router.post("/inference")
async def inference(request: Request):
    """ Your inference endpoint. Adapt this to the desired service logic. """
    pass

