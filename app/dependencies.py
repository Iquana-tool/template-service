from fastapi import Header, HTTPException

from app.state import Backend, get_backend, verify_backend_token


def get_current_backend(authorization: str = Header(default="")) -> Backend:
    """Resolve the backend associated with a bearer token."""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing backend token")

    token = authorization[7:].strip()
    if not verify_backend_token(token):
        raise HTTPException(status_code=403, detail="Invalid backend token")

    backend = get_backend(token)
    if backend is None:
        raise HTTPException(status_code=403, detail="Inactive or unknown backend token")

    return backend
