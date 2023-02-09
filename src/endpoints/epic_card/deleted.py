from src.endpoints._base import *
from src.models._base import *
import requests
import base64
import datetime
import json
import re

router = APIRouter(
    prefix="/epic_card",
    tags=["Voter Card API"]
)

VOTER_HEADERs = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-GB,en-IN;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
    "Host": "electoralsearch.in",
    "Referer": "https://electoralsearch.in/",
    "sec-ch-ua": "\"Not_A Brand\";v=\"99\", \"Google Chrome\";v=\"109\", \"Chromium\";v=\"109\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "Sec-Fetch-Dest": "image",
    "Sec-Fetch-Mode": "no-cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
}
VOTER_EPIC_REGEX = "^(([A-Z]{3}\d{7})|([A-Z]{2}\/\d{2}\/\d{3}\/\d{7}))$"


@router.get("/check_epic_card_no")
async def voter_card_no_validator(epic: str = Query()):
    if not re.match(VOTER_EPIC_REGEX, epic):
        return hcRes(detail="EPIC Card Number is Invalid", status_code=400, error=True)
    return hcRes(detail="EPIC Card Number is Valid")

@router.get("/generate_captcha/")
async def epic_captcha():
    # me: Me = Security(get_current_user, scopes=[]) 
    me = {"username": "harendra"}

    s = requests.Session()
    s.headers.update(VOTER_HEADERs)

    s.get("https://electoralsearch.in/",verify=False)

    URL = "https://electoralsearch.in/Home/GetCaptcha?image=true&id="+str("{:%a %b %d %Y %H:%M:%S} GMT+0530 (India Standard Time)".format(datetime.datetime.now()))
    
    r = s.get(URL,verify=False)
    # check if content type is application/json
    if r.headers["Content-Type"] != "application/json":
        return hcRes(detail="Captcha Not Generated", status_code=400, error=True)
    
    with open("tmp/epic/"+me["username"]+".png", "wb") as f:
        f.write(r.content)
    with open("tmp/epic/"+me["username"]+".json", "w") as f:
        DATA = {
            "COOKIE": r.cookies.get_dict(),
            "CAPTCHA": None,
            # "IMAGE": "data:image/png;base64,"+base64.b64encode(r.content).decode("utf-8"),
            "TIME" : str(datetime.datetime.now()),
        }
        f.write(json.dumps(DATA))
    
    return hcRes(detail="Captcha Generated", data = {
        # retrun base64 encoded image
        "image": "data:image/png;base64,"+base64.b64encode(r.content).decode("utf-8")
    })


@router.get("/save_captcha/{captcha}")
async def validate_captch(captcha: str):
    # me: Me = Security(get_current_user, scopes=[]) 
    me = {"username": "harendra"}
    with open("tmp/epic/"+me["username"]+".json", "r+") as f:
        data = json.loads(f.read())
        data["CAPTCHA"] = captcha
        f.seek(0)
        f.write(json.dumps(data))
        f.truncate()
    return hcRes(detail="Captcha Saved")



@router.get("/fetch_epic_data")
async def EPIC_no_Info(epic: str = Query(regex=VOTER_EPIC_REGEX)):
    # me: Me = Security(get_current_user, scopes=[]) 
    me = {"username": "harendra"}

    with open("tmp/epic/"+me["username"]+".json", "r") as f:
        data = json.loads(f.read())
        cookies = data["COOKIE"]
        captcha = data["CAPTCHA"]
    URL = "https://electoralsearch.in/Home/searchVoter"
    r = requests.post(URL,verify=False, headers=VOTER_HEADERs, cookies=cookies, data={
        "epic_no": epic,
        "page_no": 1,
        "results_per_page": 10,
        "reureureired": "ca3ac2c8-4676-48eb-9129-4cdce3adf6ea",
        "search_type": "epic",
        "state": "S24",
        "txtCaptcha": captcha
    })

    if r.text == "Wrong Captcha":
        return hcRes(detail="Wrong Captcha", error_code=100, error=True)
    
    # check if content is valid json
    try:
        JSON_DATA = json.loads(r.text)
        if "response" in JSON_DATA: 
            return hcRes(detail="EPIC Data Fetched", data=JSON_DATA["response"])
        else:
            return hcRes(detail="EPIC Data Not Fetched", error_code=400, error=True)
    except:
        return hcRes(detail="EPIC Data Not Fetched", error_code=400, error=True)

@router.get("/state_list")
async def state_list():
    URL = "https://electoralsearch.in/Home/GetStateList"
    r = requests.get(URL,verify=False, headers=VOTER_HEADERs)
    return hcRes(detail="State List Fetched", data=json.loads(r.text))

@router.get("/district_list/{st_code}")
async def district_list(st_code: str):
    URL = "https://electoralsearch.in/Home/GetDistList?st_code="+st_code
    r = requests.get(URL,verify=False, headers=VOTER_HEADERs)
    return hcRes(detail="District List Fetched", data=json.loads(r.text))

@router.get("/assembly_list/{st_code}/{dist_no}")
async def assembly_list(st_code: str, dist_no: str):
    URL = "https://electoralsearch.in/Home/GetAcList?st_code="+st_code+"&dist_no="+dist_no
    r = requests.get(URL,verify=False, headers=VOTER_HEADERs)
    return hcRes(detail="Assembly List Fetched", data=json.loads(r.text))

@router.get("/search_epic_data")
async def search_epic_data(
    age: int = Query(..., ge=18, le=120),
    gender: str = Query(..., regex="^(M|F|O)$"),
    location: str = Query(...),
    name: str = Query(...,regex="^[a-zA-Z ]+$"),
    page_no: int = Query(ge=1,default=1),
    results_per_page: int = Query(ge=1, default=10),
    rln_name: str = Query(...,regex="^[a-zA-Z ]+$")
):
    # me: Me = Security(get_current_user, scopes=[])
    me = {"username": "harendra"}

    with open("tmp/epic/"+me["username"]+".json", "r") as f:
        data = json.loads(f.read())
        cookies = data["COOKIE"]
        captcha = data["CAPTCHA"]

    
    URL = "https://electoralsearch.in/Home/searchVoter"
    r = requests.post(URL,verify=False, headers=VOTER_HEADERs, cookies=cookies, data={
        "age": age,
        "dob": None,
        "gender": gender,
        "location": location,
        "location_range" : "20",
        "name": name,
        "page_no": page_no,
        "results_per_page": results_per_page,
        "rln_name": rln_name,
        "reureureired": "ca3ac2c8-4676-48eb-9129-4cdce3adf6ea",
        "search_type": "details",
        "txtCaptcha": captcha
    })

    if r.text == "Wrong Captcha":
        return hcRes(detail="Wrong Captcha", error_code=100, error=True)

    # check if content is valid json
    try:
        JSON_DATA = json.loads(r.text)
        if "response" in JSON_DATA: 
            return hcRes(detail="EPIC Data Fetched", data=JSON_DATA["response"])
        else:
            return hcRes(detail="EPIC Data Not Fetched", error_code=400, error=True)
    except:
        return hcRes(detail="EPIC Data Not Fetched", error_code=400, error=True)
