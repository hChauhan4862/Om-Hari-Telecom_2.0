from fastapi import APIRouter, status
from hcResponseBase import hcCustomError
from src.endpoints import admin,userSelf
from src.endpoints.aadhaar import router as aadhaar_router
from src.endpoints.epic_card import router as epic_router
from src.endpoints.pan_card import router as pan_router
from src.endpoints.bhulekh import router as bhulekh_router

router = APIRouter(prefix="/api/v1", responses={
            status.HTTP_200_OK : {},
            status.HTTP_400_BAD_REQUEST: {"model": hcCustomError},
            status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized Access | Token expired or Not valid"},
            status.HTTP_403_FORBIDDEN: {"description": "Forbidden Access | Scope Not Found"},
            status.HTTP_422_UNPROCESSABLE_ENTITY: {},
            status.HTTP_429_TOO_MANY_REQUESTS: {},
        }
    )

router.include_router(admin.router)
router.include_router(userSelf.router)
router.include_router(aadhaar_router)
router.include_router(epic_router)
router.include_router(pan_router)
router.include_router(bhulekh_router)