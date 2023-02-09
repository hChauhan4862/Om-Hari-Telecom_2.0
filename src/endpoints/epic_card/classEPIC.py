import base64
import requests
from src.endpoints._base import hcRes
import json
import datetime
import os

class EPIC:
    def __init__(self, username = ""):
        self.VOTER_EPIC_REGEX = "^[a-zA-Z0-9\\/ ]{1,17}$" # epic card number regex
        self.__USERNAME = username
        self.__API_HEADERS  = {
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
    
    
    ########## GENERATING CAPTCHA ##########
    def generate_captcha(self):
        try:
            s = requests.Session()
            s.headers.update(self.__API_HEADERS)
            temp = s.get("https://electoralsearch.in/",verify=False) # just to make sure we have a session with the server and cookies
            assert temp.status_code == 200

            URL = "https://electoralsearch.in/Home/GetCaptcha?image=true&id="+str("{:%a %b %d %Y %H:%M:%S} GMT+0530 (India Standard Time)".format(datetime.datetime.now()))
            req = s.get(URL,verify=False)
            assert req.status_code == 200
            assert "application/json" in req.headers["Content-Type"]

            with open("tmp/epic/"+self.__USERNAME+".json", "w") as f:
                DATA = {
                    "COOKIE": req.cookies.get_dict(),
                    "CAPTCHA": None,
                }
                json.dump(DATA, f)
            
            return hcRes(detail="Captcha Generated", data={ # return captcha image
                "image": "data:image/png;base64,"+base64.b64encode(req.content).decode("utf-8")
            })
        except:
            pass
        return hcRes(detail="Server Error", error_code=400, error=True)

    ########## VERIFYING CAPTCHA ##########
    def verify_captcha(self, captcha):
        try:
            with open("tmp/epic/"+self.__USERNAME+".json", "r") as f:
                DATA = json.load(f)
            assert DATA["COOKIE"] != None
            if DATA["CAPTCHA"] != None:
                return hcRes(detail="Captcha Already Verified", error_code=200, error=True)

            assert self.fetch_details("S24 21", "S24", verify_captcha=captcha)

            DATA["CAPTCHA"] = captcha
            with open("tmp/epic/"+self.__USERNAME+".json", "w") as f:
                json.dump(DATA, f)

            return hcRes(detail="Captcha Verified", error_code=200, error=False)

        except:
            pass

        if not os.path.exists("tmp/epic/"+self.__USERNAME+".json"):
            return hcRes(detail="Regenerate Captcha", error_code=400, error=True)
        return hcRes(detail="Captcha Could Not Verify", error_code=403, error=True)

    ########## GETTING EPIC CARD DETAILS ##########
    def fetch_details(self, epic, state="S24", verify_captcha=False):
        try:
            with open("tmp/epic/"+self.__USERNAME+".json", "r") as f:
                DATA = json.load(f)
            
            if verify_captcha: DATA["CAPTCHA"] = verify_captcha
            assert DATA["CAPTCHA"] != None and DATA["COOKIE"] != None

            DATA_URL  = "https://electoralsearch.in/Home/searchVoter"
            POST_DATA = {
                    "epic_no": epic,
                    "page_no": 1,
                    "results_per_page": 10,
                    "reureureired": "ca3ac2c8-4676-48eb-9129-4cdce3adf6ea",
                    "search_type": "epic",
                    "state": "S24",
                    "txtCaptcha": DATA["CAPTCHA"]
            }
            req = requests.post(DATA_URL, data=POST_DATA, headers=self.__API_HEADERS, cookies=DATA["COOKIE"], verify=False)
            assert req.status_code == 200
            assert req.text != "Wrong Captcha"
            
            JSON_DATA = json.loads(req.text)
            assert "response" in JSON_DATA
            
            if verify_captcha: return True # if captcha is verified, return True

            if JSON_DATA["response"]["numFound"] == 0:
                return hcRes(detail="EX002: Epic Card Not Found", error_code=404, error=True)
            return hcRes(detail="Epic Card Details", data=JSON_DATA["response"]["docs"][0], error_code=200, error=False)

        except:
            pass
        
        if verify_captcha: return False

        # remove captcha file if exists
        if os.path.exists("tmp/epic/"+self.__USERNAME+".json"):
            os.remove("tmp/epic/"+self.__USERNAME+".json")

        return hcRes(detail="EX001: Captcha Auth Error, please regenerate captcha", error_code=403, error=True)
    
    ########## SEARCHING EPIC CARD DETAILS ##########
    def search_details(self,name,relative_name, age, location, page_no=1 ):
        try:
            with open("tmp/epic/"+self.__USERNAME+".json", "r") as f:
                DATA = json.load(f)
            assert DATA["CAPTCHA"] != None and DATA["COOKIE"] != None

            DATA_URL  = "https://electoralsearch.in/Home/searchVoter"
            POST_DATA = {
                "age": age,
                "dob": None,
                "gender": None,
                "location": location,
                "location_range" : "20",
                "name": name,
                "page_no": page_no,
                "results_per_page": 10,
                "rln_name": relative_name,
                "reureureired": "ca3ac2c8-4676-48eb-9129-4cdce3adf6ea",
                "search_type": "details",
                "txtCaptcha": DATA["CAPTCHA"]
            }
            req = requests.post(DATA_URL, data=POST_DATA, headers=self.__API_HEADERS, cookies=DATA["COOKIE"], verify=False)
            assert req.status_code == 200
            assert req.text != "Wrong Captcha"
            
            JSON_DATA = json.loads(req.text)
            assert "response" in JSON_DATA

            if JSON_DATA["response"]["numFound"] == 0:
                return hcRes(detail="EX002: Record Not Found", error_code=404, error=True)
            return hcRes(detail="Epic Records", data=JSON_DATA["response"], error_code=200, error=False)

        except:
            pass
        
        # remove captcha file if exists
        if os.path.exists("tmp/epic/"+self.__USERNAME+".json"):
            os.remove("tmp/epic/"+self.__USERNAME+".json")

        return hcRes(detail="EX001: Captcha Auth Error, please regenerate captcha", error_code=403, error=True)
    
    
    def fetchState(self):
        try:
            URL = "https://electoralsearch.in/Home/GetStateList"
            req = requests.get(URL,verify=False, headers=self.__API_HEADERS)
            assert req.status_code == 200
            assert "application/json" in req.headers["Content-Type"]
            return hcRes(detail="State List", data=req.json(), error_code=200, error=False)
        except Exception as e:
            pass
        return hcRes(detail="Server Error", error_code=400, error=True)
    
    def fetchDistrict(self, state):
        try:
            URL = "https://electoralsearch.in/Home/GetDistList?st_code="+state
            req = requests.get(URL,verify=False, headers=self.__API_HEADERS)
            assert req.status_code == 200
            assert "application/json" in req.headers["Content-Type"]
            return hcRes(detail="District List", data=req.json(), error_code=200, error=False)
        except:
            pass
        return hcRes(detail="Server Error", error_code=400, error=True)
    
    def fetchAssembly(self, state, district):
        try:
            URL = "https://electoralsearch.in/Home/GetAcList?st_code={}&dist_no={}".format(state, district)
            req = requests.get(URL,verify=False, headers=self.__API_HEADERS)
            assert req.status_code == 200
            assert "application/json" in req.headers["Content-Type"]
            return hcRes(detail="Assembly List", data=req.json(), error_code=200, error=False)
        except:
            pass
        return hcRes(detail="Server Error", error_code=400, error=True)