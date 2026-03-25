from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.state import verify_backend_token
import logging

logger = logging.getLogger(__name__)

class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware to validate API key in requests."""

    async def dispatch(self, request: Request, call_next):
        # Skip authentication for registration and health endpoints
        if request.url.path in ["/docs", "/openapi.json", "/item", "/health", "/register"]:
            return await call_next(request)
        
        # Skip for public endpoints
        if request.url.path.startswith("/docs") or request.url.path.startswith("/openapi"):
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        token = None
        if auth_header.lower().startswith("bearer "):
            token = auth_header[7:].strip()

        if not token or not verify_backend_token(token):
            logger.warning("Request with missing or invalid backend token")
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing or invalid backend token"}
            )

        return await call_next(request)