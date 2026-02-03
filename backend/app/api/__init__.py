"""
API module with auto-discovery of versioned routers.

This module automatically discovers all version folders (v1, v2, etc.)
and includes their routers into the main API router.
"""

from fastapi import APIRouter
from pathlib import Path
import importlib.util

# Create the main API router
router = APIRouter()

# Get the directory of this file
_api_dir = Path(__file__).parent

# Auto-discover all version folders (v1, v2, v3, etc.)
_version_dirs = sorted([d for d in _api_dir.iterdir() if d.is_dir() and d.name.startswith("v")])

for _version_dir in _version_dirs:
    # Load the __init__.py from each version folder
    _version_init = _version_dir / "__init__.py"
    
    if _version_init.exists():
        _module_name = f"app.api.{_version_dir.name}"
        
        # Load the module dynamically
        _spec = importlib.util.spec_from_file_location(_module_name, _version_init)
        _module = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_module)
        
        # Include the router from the version module
        if hasattr(_module, "router"):
            router.include_router(_module.router)


# ==================== Root & Health ====================
@router.get("/", tags=["root"])
async def root() -> dict:
    return {
        "message": "Smart Audit Agent backend is running",
        "docs": "/docs",
        "api_version": "v1",
    }


@router.get("/health", tags=["health"])
async def health() -> dict:
    return {"status": "ok"}


__all__ = ["router"]
