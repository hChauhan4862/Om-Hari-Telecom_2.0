from src.endpoints._base import *
from src.models._base import *
import requests
from src.endpoints.aadhaar.uid_validator import is_uid
import re

router = APIRouter(
    prefix="/pan_card",
    tags=["PAN Card API"]
)

PAN_CARD_REGEX = "^[A-Z]{5}[0-9]{4}[A-Z]{1}$"

@router.get("/check_pan_card_no/{pan_card_no}")
async def check_pan_formate(pan_card_no: str):
    if not re.match(PAN_CARD_REGEX, pan_card_no):
        return hcRes(detail="PAN Card Number is Invalid", error_code=400, error=True)
    return hcRes(detail="PAN Card Number is Valid")

@router.get("/pan_status/{pan_card_no}")
async def check_pan_no_status(pan_card_no: str):
    URL = "https://app-moneyview.whizdm.com/loans/services/api/lending/nsdl"
    req = requests.post(URL, data={"pan": pan_card_no}, verify=False, headers={"x-mv-app-version":"433"})
    if req.status_code == 200:
        return hcRes(detail="Status Fatched Success", data=req.json())

@router.get("/check_aadhaar_exist/{aadhaar}")
async def pan_by_aadhaar(aadhaar: str):
    if not is_uid(aadhaar):
        return hcRes(detail="Aadhaar Number is Invalid", error_code=400, error=True)

    URL = "https://www.myutiitsl.com/PANform/forms/pan.html/aadhaarPanLinkInfo"
    data = {
        "aadhaarNo": aadhaar
    }
    r = requests.post(URL, data=data, verify=False, headers={
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-GB,en-IN;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Host": "www.myutiitsl.com",
        "Origin": "https://www.myutiitsl.com",
        "Referer": "https://www.myutiitsl.com/PANform/forms/pan.html/mainForm",
        "sec-ch-ua": "\"Not_A Brand\";v=\"99\", \"Google Chrome\";v=\"109\", \"Chromium\";v=\"109\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    })
    if r.status_code == 200:
        return hcRes(detail="Status Fatched Success", data={"msg": r.text})
    pass
