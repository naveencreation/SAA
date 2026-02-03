"""
API v1 routes auto-discovery module.

This module automatically discovers and includes all route files ending with `_routes.py`
in the v1 folder, making it easy to add new endpoints without manual registration.
"""

from fastapi import APIRouter
from pathlib import Path
import importlib.util

# Create the router for all v1 endpoints
router = APIRouter(prefix="/api/v1", tags=["v1"])

# Get the directory of this file
_v1_dir = Path(__file__).parent

# Auto-discover all *_routes.py files
_route_files = sorted(_v1_dir.glob("*_routes.py"))

for _route_file in _route_files:
    # Get module name from filename (e.g., "auth_routes.py" -> "auth_routes")
    _module_name = _route_file.stem
    
    # Load the module dynamically
    _spec = importlib.util.spec_from_file_location(_module_name, _route_file)
    _module = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_module)
    
    # Include the router from the module if it has one
    if hasattr(_module, "router"):
        router.include_router(_module.router)

__all__ = ["router"]
