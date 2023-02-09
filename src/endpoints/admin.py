from src.endpoints._base import *
from src.models.admin import *

#APIRouter creates path operations for item module
router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

