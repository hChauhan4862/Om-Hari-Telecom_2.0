from src.endpoints._base import *
from src.models._base import *
# from src.endpoints.bhulekh.village_updater import update_villages_list_task
from src.endpoints.bhulekh.bhulekhClass import hcBhulekh
import datetime


router = APIRouter(
    prefix="/bhulekh",
    tags=["Bhulekh API"]
)

@router.get("/search_village/{search_text}")
async def village_search(search_text: str = Path(...,min_length=1)):
    return hcBhulekh().village_search_json(search_text)

@router.get("/search_village/{search_text}/{offset}")
async def village_search_info(search_text: str = Path(...,min_length=2), offset: int = Path(ge=0)):
    return hcBhulekh().village_search_json(search_text, offset)

@router.get("/village/{village_code}")
async def village_info_view(village_code: int = Path(le=999999,ge=100000)):
    return hcBhulekh().village_search_json(village_code)

@router.get("/search_gata/{village_code}/{gata_no}")
async def gata_wise_search(village_code: int = Path(le=999999,ge=100000), gata_no: str = Path()):
    return hcBhulekh().list_search(village_code=village_code, act="sgw", value=gata_no)

@router.get("/search_khata/{village_code}/{khata_no}")
async def khata_wise_search(village_code: int = Path(le=999999,ge=100000), khata_no: int = Path(gt=0)):
    khata_no = str(khata_no).zfill(5)
    return hcBhulekh().list_search(village_code=village_code, act="sbacn", value=khata_no)

@router.get("/search_name/{village_code}/{name}")
async def name_wise_search(village_code: int = Path(le=999999,ge=100000), name: str = Path()):
    return hcBhulekh().list_search(village_code=village_code, act="sbname", value=name)


@router.get("/khata/{village_code}/{khata_no}")
async def get_khata(village_code: int = Path(le=999999,ge=100000), khata_no: int = Path(...,le=99999)):
    return hcBhulekh().khata_json(khata_no, village_code)

@router.get("/ansh/{village_code}/{khata_no}")
async def get_khata_ansh(village_code: int = Path(le=999999,ge=100000), khata_no: int = Path(...,le=99999)):
    return hcBhulekh().ansh_json(khata_no, village_code)

# @router.get("/updateVillageList")
# async def update_villages_list(background_tasks: BackgroundTasks):
#     lastRorVillageUpdateTime = db.query(configSettings).filter(configSettings.key == "lastRorVillageUpdateTime").first()
#     lastRorVillageUpdateTimeStart = db.query(configSettings).filter(configSettings.key == "lastRorVillageUpdateTimeStart").first()
#     if not lastRorVillageUpdateTime:
#         lastRorVillageUpdateTime = configSettings(key="lastRorVillageUpdateTime", value="0")
#         db.add(lastRorVillageUpdateTime)
#         db.commit()
#     if not lastRorVillageUpdateTimeStart:
#         lastRorVillageUpdateTimeStart = configSettings(key="lastRorVillageUpdateTimeStart", value="0")
#         db.add(lastRorVillageUpdateTimeStart)
#         db.commit()
    
#     # check if last update was more than 24 hours ago
#     if float(lastRorVillageUpdateTime.value) < (datetime.datetime.now() - datetime.timedelta(hours=48)).timestamp():
#         # check if last update was more than 2 hours ago
#         if float(lastRorVillageUpdateTimeStart.value) < (datetime.datetime.now() - datetime.timedelta(hours=1)).timestamp():
#             lastRorVillageUpdateTimeStart.value = str(datetime.datetime.now().timestamp())
#             db.commit()

#             background_tasks.add_task(hcBhulekh(db).update_villages_list_task)
#             print("Starting update")
#             return hcRes(detail="Update started in background")
#         else:
#             return hcRes(detail="Update already started, please wait for 1 hours",error=True,error_code=100)
#     else:
#         return hcRes(detail="Update already completed, please wait for 48 hours",error=True,error_code=101, data = {
#             "lastUpdate": "{:%Y-%m-%d %H:%M:%S}".format(datetime.datetime.fromtimestamp(float(lastRorVillageUpdateTime.value))),
#             "lastUpdateStart": "{:%Y-%m-%d %H:%M:%S}".format(datetime.datetime.fromtimestamp(float(lastRorVillageUpdateTimeStart.value))),
#             "total_time": str(datetime.datetime.fromtimestamp(float(lastRorVillageUpdateTime.value)) - datetime.datetime.fromtimestamp(float(lastRorVillageUpdateTimeStart.value))),
#             "vilage_count": db.query(bhulekhVillages).count()

#         })