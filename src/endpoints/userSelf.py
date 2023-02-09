from src.endpoints._base import *
from src.models.userSelf import *

#APIRouter creates path operations for item module
router = APIRouter(
    prefix="/me",
    tags=["Authorisation"]
)

@router.get("/info", responses={200: {"model": hcOutput}})
async def get_self_Info(request: Request, me: Me = Security(get_current_user, scopes=[""])):
    return hcRes(data={'uid':me.uid,'role':me.role,'username':me.username})
