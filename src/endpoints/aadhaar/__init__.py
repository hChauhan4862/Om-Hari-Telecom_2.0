from src.endpoints._base import *
from src.models._base import *
from .uid_validator import is_uid
from src.endpoints.aadhaar.classAadhaarPDF import AadhaarPDF
import requests

router = APIRouter(
    prefix="/aadhaar",
    tags=["Aadhaar API"]
)

@router.get("/check_uid/{uid}")
async def uid_validator(uid: str):
    if not is_uid(uid):
        raise hcCustomException(detail="Invalid Aadhaar Number", status_code = 400)
    return hcRes(detail="Valid Aadhaar Number")

####### [:START:] API to fetch aadhaar data from Database #######

@router.get("/all_list")
async def all_aadhaar_list_in_database():
    return hcRes(detail="success",data=deta_obj.db.aadhaar_originalsFetch())

@router.get("/search_uid/{uid}")
async def all_copy_of_aadhaar_no(uid: str):
    if not is_uid(uid):
        raise hcCustomException(detail="Invalid Aadhaar Number", status_code = 400)
    return hcRes(detail="success",data=deta_obj.db.aadhaar_originalsFetch(UID=uid))

@router.get("/json/{key}")
async def aadhaar_json_by_key(key: str):
    if len(key) != 12:
        raise hcCustomException(detail="Invalid Aadhaar Unique Key", status_code = 400)
    data = deta_obj.db.aadhaar_originalsFetch(key=key)
    if len(data) == 0:
        raise hcCustomException(detail="Aadhaar not found", status_code = 404)
    data = data[0]
    return hcRes(detail="success",data=data)

@router.get("/images/{key}.jpg")
async def aadhaar_image_by_key(key: str):
    try:
        assert len(key) == 12, "Invalid Aadhaar Unique Key"
        file = deta_obj.files.aadhaar_originals.get(key)
        return StreamingResponse(BytesIO(file.read()), media_type="image/jpeg")
    except Exception as e:
        raise hcCustomException(detail="File not found", status_code = 404)

@router.get("/qr/{key}.jpg")
async def aadhaar_qr_by_key(key: str):
    try:
        assert len(key) == 12, "Invalid Aadhaar Unique Key"
        data = deta_obj.db.aadhaar_originalsFetch(key=key)
        assert len(data) > 0, "Aadhaar not found"
        data = data[0]

        TEXT = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<PrintLetterBarcodeData "
        TEXT += 'uid="' + data['UID'] + '" '
        TEXT += 'name="' + data['Name'] + '" '
        TEXT += 'gender="' + data['Gender'] + '" ' if "Gender" in data and data["Gender"] != None and data["Gender"] != "" else ""
        TEXT += 'yob="' + data['DOB'].split("-")[0] + '" ' if "DOB" in data and data["DOB"] != None and data["DOB"] != "" else ""
        TEXT += 'co="' + data['CareOf'] + '" ' if "CareOf" in data and data["CareOf"] != None and data["CareOf"] != "" else ""
        TEXT += 'loc="' + data['Locality'] + '" ' if "Locality" in data and data["Locality"] != None and data["Locality"] != "" else ""
        TEXT += 'vtc="' + data['VillageTown'] + '" ' if "VillageTown" in data and data["VillageTown"] != None and data["VillageTown"] != "" else ""
        TEXT += 'po="' + data['PostOffice'] + '" ' if "PostOffice" in data and data["PostOffice"] != None and data["PostOffice"] != "" else ""
        TEXT += 'dist="' + data['District'] + '" ' if "District" in data and data["District"] != None and data["District"] != "" else ""
        TEXT += 'subdist="' + data['SubDistrict'] + '" ' if "SubDistrict" in data and data["SubDistrict"] != None and data["SubDistrict"] != "" else ""
        TEXT += 'state="' + data['State'] + '" ' if "State" in data and data["State"] != None and data["State"] != "" else ""
        TEXT += 'pc="' + data['PinCode'] + '" ' if "PinCode" in data and data["PinCode"] != None and data["PinCode"] != "" else ""
        TEXT += 'yob="' + "/".join(data['DOB'].split("-")) + '" ' if "DOB" in data and data["DOB"] != None and data["DOB"] != "" else ""
        TEXT += "/>"
        from qrcode import QRCode

        qr = QRCode(version=1, box_size=2, border=1)
        qr.add_data(TEXT)
        qr.make(fit=True)
        # Generate the QR code image
        img = qr.make_image(fill_color="black", back_color="white")
        # Resize the image to 70x70 pixels
        # img = img.resize((70, 70))

        # Save the image to a file
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        
        return StreamingResponse(buffer, media_type="image/jpeg")
    except Exception as e:
        print(e)
        raise hcCustomException(detail="File not found", status_code = 404)

####### [:END:] API to fetch aadhaar data from Database #######


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
