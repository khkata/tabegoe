from fastapi import APIRouter

from .users import router as users_router
from .groups import router as groups_router
from .hearings import router as hearings_router
from .recommendations import router as recommendations_router
# 段階的に機能を有効化
try:
    from .interviews import router as interviews_router
    INTERVIEWS_AVAILABLE = True
except Exception as e:
    print(f"Interviews module not available: {e}")
    INTERVIEWS_AVAILABLE = False

api_router = APIRouter()

api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(groups_router, prefix="/groups", tags=["groups"])
api_router.include_router(hearings_router, prefix="/hearings", tags=["hearings"])
api_router.include_router(recommendations_router, prefix="/recommendations", tags=["recommendations"])

if INTERVIEWS_AVAILABLE:
    api_router.include_router(interviews_router, prefix="/interviews", tags=["interviews"])