from src.endpoints._base import *
from src.models._base import *
from src.endpoints.epic_card.classEPIC import EPIC

router = APIRouter(
    prefix="/epic_card",
    tags=["Voter Card API"]
)

VOTER_EPIC_REGEX = "^[a-zA-Z0-9\\/ ]{1,17}$"

@router.get("/generate_captcha/")
async def epic_captcha():
    # me: Me = Security(get_current_user, scopes=[])
    me: Me = MeObj(username="harendra",uid=0,role="TEST_USER",db=None) # for testing purpose only
    return EPIC(me.username).generate_captcha()

@router.get("/verify_captcha/")
async def epic_captcha_verify(captcha: str = Query(...)):
    # me: Me = Security(get_current_user, scopes=[])
    me: Me = MeObj(username="harendra",uid=0,role="TEST_USER",db=None) # for testing purpose only
    return EPIC(me.username).verify_captcha(captcha)

@router.get("/fetch_details/")
async def epic_fetch_details(epic: str = Query(...), state: str = Query(default="S24") ):
    # me: Me = Security(get_current_user, scopes=[])
    me: Me = MeObj(username="harendra",uid=0,role="TEST_USER",db=None) # for testing purpose only
    return EPIC(me.username).fetch_details(epic, state)

@router.get("/search/")
async def epic_search(name: str = Query(), relative_name: str = Query(), age: int = Query(ge=18), location: str = Query(example="S24,9,",regex="^[A-Z]?[0-9]+,[0-9]*,[0-9]*$"), page_no: int = Query(default=1,ge=1) ):
    # me: Me = Security(get_current_user, scopes=[])
    me: Me = MeObj(username="harendra",uid=0,role="TEST_USER",db=None)
    return EPIC(me.username).search_details(name=name,relative_name=relative_name,age=age,location=location,page_no=page_no)

@router.get("/state_list/")
async def state_list():
    return EPIC().fetchState()

@router.get("/district_list/{st_code}")
async def district_list(st_code: str):
    return EPIC().fetchDistrict(st_code)

@router.get("/assembly_list/{st_code}/{dt_code}")
async def assembly_list(st_code: str, dt_code: str):
    return EPIC().fetchAssembly(st_code, dt_code)

