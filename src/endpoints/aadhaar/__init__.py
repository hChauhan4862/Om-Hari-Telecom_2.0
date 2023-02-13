from src.endpoints._base import *
from src.models._base import *
from .uid_validator import is_uid
from src.endpoints.aadhaar.classAadhaarPDF import AadhaarPDF
from fastapi import BackgroundTasks
import requests
import os

router = APIRouter(
    prefix="/aadhaar",
    tags=["Aadhaar API"]
)

def updatePDFList(db: Session):
    AADHAAR_DIR = "tmp/AADHAAR_FILES"
    for file in os.listdir(AADHAAR_DIR):
        # skip if file is directory
        if os.path.isdir(AADHAAR_DIR+"/"+file): continue
        print("RUNNING FOR :: ",file, " :: ", end="")
        try:
            with open(AADHAAR_DIR+"/"+file, "rb") as f:
                aadhaar = AadhaarPDF(f,password="202132", bruteForce=True)
                json = aadhaar.get()
                assert json, "FAILED"
        except Exception as e:
            # move file rename to AADHAAR_DIR/error/{file}.pdf
            if str(e) != "Could not brute force the password":
                os.rename(AADHAAR_DIR+"/"+file, AADHAAR_DIR+"/error/"+file)
            print(e)
            continue
        EXIST = db.query(aadhaar_pdf).filter(aadhaar_pdf.UID == json.UID).first()
        if EXIST:
            # compare download date and delete if older by converting to datetime
            if not json.DownloadDate or EXIST.DownloadDate < datetime.datetime.strptime(json.DownloadDate, "%Y-%m-%d").date():
                db.delete(EXIST)
                db.commit()
            else:
                # move file rename to AADHAAR_DIR/done/{name} {yob}{pinCode}-{uid} {datetimeepoch}.pdf
                yob = json.DOB.split("-")[0]
                newFileName = f"{json.Name} {yob} {json.PinCode}-{json.UID} {datetime.datetime.now().timestamp()}.pdf"
                os.rename(AADHAAR_DIR+"/"+file, AADHAAR_DIR+"/done/"+newFileName)
                continue
        # add to db
        db.add(aadhaar_pdf(**(dict(json.__dict__))))
        db.commit()

        # move file rename to AADHAAR_DIR/done/{name} {yob}{pinCode}-{uid} {datetimeepoch}.pdf
        yob = json.DOB.split("-")[0]
        newFileName = f"{json.Name} {yob} {json.PinCode}-{json.UID} {datetime.datetime.now().timestamp()}.pdf"
        os.rename(AADHAAR_DIR+"/"+file, AADHAAR_DIR+"/done/"+newFileName)
        print("SUCCESS")

@router.get("/updatePDFList")
async def test_page(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    background_tasks.add_task(updatePDFList, db)
    return hcRes(detail="Updating PDF List")

@router.get("/check_uid/{uid}")
async def uid_validator(uid: str):
    if not is_uid(uid):
        raise hcCustomException(detail="Invalid Aadhaar Number", status_code = 400)
    return hcRes(detail="Valid Aadhaar Number")


class verify_uid_req(BaseModel):
    uid: str = Field(..., example="922302970901", description="Aadhaar Number", min_length=12, max_length=12, regex="^[0-9]*$",)
    name: str = Field(..., example="Harendra Chauhan", description="Name as per Aadhaar", min_length=3, max_length=100)
    gender: str = Field(..., regex="^(M|F|T){1}$")


@router.post("/demographicAuth")
async def demographic_auth(form: verify_uid_req):
    if not is_uid(form.uid):
        raise hcCustomException(detail="Invalid Aadhaar Number", status_code = 400)
    
    # create session for request
    s = requests.Session()
    s.headers.update({
        'Host': 'www.scholarships.punjab.gov.in',
        'Connection': 'keep-alive',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-GB,en-IN;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'max-age=0',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://www.scholarships.punjab.gov.in',
        'Referer': 'https://www.scholarships.punjab.gov.in/public/AadharAuthenticationaspx.aspx',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    })

    # get request
    r = s.get("https://www.scholarships.punjab.gov.in/public/AadharAuthenticationaspx.aspx",verify=False)
    if r.status_code != 200:
        raise hcCustomException(detail="Aadhaar API is not working", status_code = 500)
    
    viewstate = r.text.split('id="__VIEWSTATE" value="')[1].split('"')[0]
    viewstategenerator = r.text.split('id="__VIEWSTATEGENERATOR" value="')[1].split('"')[0]

    # post request
    r = s.post("https://www.scholarships.punjab.gov.in/public/AadharAuthenticationaspx.aspx",verify=False, data={
        '__EVENTTARGET': 'ctl00$dpPH$txtAadhaarNumber',
        '__EVENTARGUMENT': '',
        '__LASTFOCUS': '',
        '__VIEWSTATE': viewstate,
        '__VIEWSTATEGENERATOR': viewstategenerator,
        'ctl00$dpPH$txtAadhaarNumber': form.uid,
        'ctl00$dpPH$txtname': form.name,
        'ctl00$dpPH$ddlGender': form.gender,
        'ctl00$dpPH$txtVerifyCaptcha': 'TbjYsh',
        'ctl00$dpPH$btnCheckAuthentication': 'Authenticate',
        'ctl00$hdnisauthendicate': '0'
    })

    if r.status_code != 200:
        raise hcCustomException(detail="Aadhaar API is not working", status_code = 500)

    if "SucessShowPopup();" in r.text:
        return hcRes(detail="Aadhaar Verified")
    elif 'ShowPopup();' in r.text:
        error = r.text.split('<span id="ctl00_dpPH_lblmsg" style="color:Red;font-size:15px;">')[1].split('</span>')[0]
        raise hcCustomException(detail=error, status_code = 400)
    else:
        raise hcCustomException(detail="Could Not Verify", status_code = 500)
