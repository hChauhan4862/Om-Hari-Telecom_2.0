import requests
from bs4 import BeautifulSoup
from sqlalchemy.sql.expression import func
import datetime
from src.endpoints._base import hcRes
from db import deta_obj
import re


class hcBhulekh:
    def __init__(self) -> None:
        self.__base_url = "https://upbhulekh.gov.in/public/public_ror/"
    
    def village_search_json(self, search_keyword, offset=0):
        
        if isinstance(search_keyword, int):
            # search by village code
            villages = deta_obj.db.ror_villagesLists(village_code=search_keyword)
            return hcRes(data=villages)
        
        # top 50 search by village name
        villages = deta_obj.db.ror_villagesLists(village_name=search_keyword)[offset:offset+50]
        return hcRes(data=villages)
    
    def list_search(self,village_code,act,value):
        if value == " ":
            value = ""
        types = {
            "sgw": "kcn",   # Gata wise Name Information
            "sbacn": "acn", # Khata Number wise Name Information
            "sbname": "name",   # Name wise Khata Number Information
        }
        print("act={}&vcc={}&{}={}".format(act,village_code,types[act],value))
        req = self.__get_data("act={}&vcc={}&{}={}&fasli-code-value=999".format(act,village_code,types[act],value),json=True)
        return hcRes(data=req)

    def khata_json(self, khata_no, village_code):
        # pad 0 to khata_no
        khata_no = str(khata_no).zfill(5)
        VILLAGE_INFO = deta_obj.db.ror_villagesLists(village_code=village_code)
        VILLAGE_INFO = VILLAGE_INFO[0] if len(VILLAGE_INFO) else None
        if not VILLAGE_INFO:
            return hcRes(detail="Village not found",error=True,error_code=404)
        if not VILLAGE_INFO.flag_khatauni and not VILLAGE_INFO.flag_ansh and not VILLAGE_INFO.flag_rtk:
            return hcRes(detail="Details not available for this village",error=True,error_code=404)
        
        DATA = {
            "META_INFO": VILLAGE_INFO.__dict__,
            "LAND_OWNERS": [],
            "LAND_DETAILS": [],
            "ORDERS": [],
            "COMMENTS": [],
        }

        # get khata data
        soup = self.__get_data("public_ror_report.jsp?khata_number={}&village_code={}".format(khata_no, village_code))
        # parse khata data
        table = soup.find("table", {"class": "report"})
        if not table:
            return hcRes(detail="Could Not Connect With API",error=True,error_code=400)
        
        PART_NO = table.find("label", {"name": "bhaagName"}).text.strip()
        FASLI_YEAR = table.find("label", {"name": "fasliVarsh"}).text.strip()
        SHRENI = table.find("label", {"name": "typeCaptionDetail"}).text.strip()

        if SHRENI in ["","/"]:
            return hcRes(detail="Khata Not Found",error=True,error_code=404)
        
        # Main table of khata data
        tbody = table.find("tbody")
        tr = tbody.find_all("tr")[2]
        tds = tr.find_all("td")

        # find labels under first td
        name_labels = tds[0].find_all("label",{"class":"ForTranslation"})
        for label in name_labels:
            name = label.text
            NAME = {
                "name": name.split(" /")[0],
                "father_name": name.split(" /")[1],
                "address": name.split(" /")[2],
            }
            DATA["LAND_OWNERS"].append(NAME)
        
        gata_links = tds[1].find_all("a")
        area_text = re.findall(r"[0-9\.]{6}",tds[2].prettify())
        for i in range(len(gata_links)):
            link = gata_links[i]
            gata_no = link.text.replace("\n","").strip()
            uniqueCode = link["href"].split("uniqueCode=")[1].split("&")[0]

            GATA = {
                "gata_no": gata_no,
                "unique_id": uniqueCode,
                "area": float(area_text[i]),
            }
            DATA["LAND_DETAILS"].append(GATA)
        
        # get orders
        orders = tds[3].find("span").prettify().replace("<span>","").replace("</span>","").replace("\n ","").split("<br/><br/>")
        DATA["ORDERS"] = [order.strip() for order in orders if order.strip() != ""]

        # get comments
        comments = tds[4].find("span").prettify().replace("<span>","").replace("</span>","").replace("\n ","").split("<br/><br/>")
        DATA["COMMENTS"] = [comment.strip() for comment in comments if comment.strip() != ""]


        # OTHER DATA
        tr = tbody.find_all("tr")[3]
        tds = tr.find_all("td")
        TOTAL_GATA = tds[1].text.strip()
        TOTAL_AREA = tds[2].text.strip()

        DATA["META_INFO"]["total_gata"] = float(TOTAL_GATA)
        DATA["META_INFO"]["total_area"] = float(TOTAL_AREA)
        DATA["META_INFO"]["part_no"] = PART_NO
        DATA["META_INFO"]["fasli_year"] = FASLI_YEAR
        DATA["META_INFO"]["Land_Type"] = SHRENI.split("/")[0].strip()
        DATA["META_INFO"]["Land_Type_Desc"] = SHRENI.split("/")[1].strip()

        # return output
        OP = {
            "khata_number": khata_no,
            "village_code": village_code,
            "khata_data": DATA
        }
        return hcRes(data=OP)

        pass


    ###########################################################################################################


    def ansh_json(self, khata_no, village_code):
        # pad 0 to khata_no
        khata_no = str(khata_no).zfill(5)
        VILLAGE_INFO = deta_obj.db.ror_villagesLists(village_code=village_code)
        VILLAGE_INFO = VILLAGE_INFO[0] if len(VILLAGE_INFO) else None

        if not VILLAGE_INFO:
            return hcRes(detail="Village not found",error=True,error_code=404)
        if not VILLAGE_INFO.flag_ansh and not VILLAGE_INFO.flag_rtk:
            return hcRes(detail="Details not available for this village",error=True,error_code=404)

        DATA = {
            "META_INFO": VILLAGE_INFO.__dict__,
            "LAND_OWNERS": [],
            "ORDERS": [],
            "COMMENTS": [],
        }

        # get khata data
        html = self.__get_data("public_ror_report_ansh.jsp?khata_number={}&village_code={}".format(khata_no, village_code), html=True)
        
        # parse khata data
        FASLI_YEAR = self.find_between(html, "<b>फसली वर्ष :</b>", "</div>")
        if FASLI_YEAR == "Fasli Year" or FASLI_YEAR == "":
            return hcRes(detail="Khata Not Found",error=True,error_code=404)
        
        ERROR = self.find_between(html, '<div style="font-size: 20px; padding: 5px 0px 0px 5px;">', '</div>',True)
        if len(ERROR) >= 2:
            ERROR = ERROR[1].replace("&nbsp;"," ").strip()
            return hcRes(detail=ERROR,error=True,error_code=400)


        PART_NO = self.find_between(html, '<b>भाग :</b>', '</div>')
        SHRENI = self.find_between(html, '<b>श्रेणी :</b>', '</td>')

        # scrape data
        info = self.find_between(html, '<span style="line-height: 22px;">', '</span>',True)
        NAMES_LIST = info[0].split("<br>")[:-1]
        GATAs_LIST = info[1].split("<br>")[:-1]
        AREAs_LIST = info[2].split("<br>")[:-1]
        ANSHs_LIST = info[3].split("<br>")[:-1]

        FINAL_NAMES = [{} for i in range(len(NAMES_LIST)) if NAMES_LIST[i].strip() != ""]

        name_index = -1
        for i in range(len(NAMES_LIST)):
            if NAMES_LIST[i].strip() != "":
                name_index += 1
                FINAL_NAMES[name_index]["name"] = NAMES_LIST[i].split(" /")[0]
                FINAL_NAMES[name_index]["father_name"] = NAMES_LIST[i].split(" /")[1]
                FINAL_NAMES[name_index]["address"] = NAMES_LIST[i].split(" /")[2]
                FINAL_NAMES[name_index]["total_ansh"] = 0
                FINAL_NAMES[name_index]["LAND_DETAILS"] = []
            
            FINAL_NAMES[name_index]["total_ansh"] += float(ANSHs_LIST[i])
            FINAL_NAMES[name_index]["LAND_DETAILS"].append({
                "gata_no": GATAs_LIST[i].split("(")[0],
                "unique_id": GATAs_LIST[i].split("(")[1].replace(")",""),
                "area": float(AREAs_LIST[i]),
                "ansh": float(ANSHs_LIST[i])
            })

        DATA["META_INFO"]["total_gata"] = len(FINAL_NAMES[0]["LAND_DETAILS"])
        DATA["META_INFO"]["total_area"] = sum(d["area"] for d in FINAL_NAMES[0]["LAND_DETAILS"] if "area" in d)

        DATA["META_INFO"]["part_no"] = PART_NO
        DATA["META_INFO"]["fasli_year"] = FASLI_YEAR
        DATA["META_INFO"]["Land_Type"] = SHRENI.split("/")[0].strip()
        DATA["META_INFO"]["Land_Type_Desc"] = SHRENI.split("/")[1].strip().replace("  "," ")

        DATA["LAND_OWNERS"] = FINAL_NAMES

        OP = {
            "khata_number": khata_no,
            "village_code": village_code,
            "khata_data": DATA
        }
        return hcRes(data=OP)

    ###########################################################################################################

    # def update_villages_list_task(self):
    #     print("Updating villages list")
    #     VILLAGES = {}
    #     # get all districts
    #     try:
    #         districts = self.__get_data("act=fillDistrict", json=True)
    #         for district in districts:
    #             print("NORMAL: ",district["district_name_english"])
    #             # get all tehsils
    #             tehsils = self.__get_data("act=fillTehsil&district_code=" + district["district_code_census"], json=True)
    #             for tehsil in tehsils:
    #                 # get all villages
    #                 villages = self.__get_data("act=fillVillage&district_code=" + district["district_code_census"] + "&tehsil_code=" + tehsil["tehsil_code_census"], json=True)
    #                 for village in villages:
    #                     INDEX = "{}/{}/{}".format(district["district_code_census"], tehsil["tehsil_code_census"], village["village_code_census"])
    #                     if INDEX not in VILLAGES:
    #                         VILLAGES[INDEX] = {}

    #                     VILLAGES[INDEX].update({
    #                         # "index": INDEX,
    #                         "district_name": district["district_name_english"],
    #                         "district_code": district["district_code_census"],
    #                         "district_hindi": district["district_name"],

    #                         "tehsil_name": tehsil["tehsil_name_english"],
    #                         "tehsil_code": tehsil["tehsil_code_census"],
    #                         "tehsil_hindi": tehsil["tehsil_name"],

    #                         "village_name": village["vname_eng"],
    #                         "village_code": village["village_code_census"],
    #                         "village_hindi": village["vname"],

    #                         "paragna_hindi": village["pname"],
    #                         "paragna_code": village["pargana_code_new"],

    #                         "flag_survey": 0 if village["flg_survey"] == "N" else 1,
    #                         "flag_chakbandi": 0 if village["flg_chakbandi"] == "N" else 1,

    #                         "flag_khatauni": 1
    #                     })
                        
    #         districts = self.__get_data("act=fillDistrictAnsh", json=True)
    #         for district in districts:
    #             print("ANSH: ",district["district_name_english"])
    #             # get all tehsils
    #             tehsils = self.__get_data("act=fillTehsilAnsh&district_code=" + district["district_code_census"], json=True)
    #             for tehsil in tehsils:
    #                 # get all villages
    #                 villages = self.__get_data("act=fillVillageAnsh&district_code=" + district["district_code_census"] + "&tehsil_code=" + tehsil["tehsil_code_census"], json=True)
    #                 for village in villages:
    #                     INDEX = "{}/{}/{}".format(district["district_code_census"], tehsil["tehsil_code_census"], village["village_code_census"])
    #                     if INDEX not in VILLAGES:
    #                         VILLAGES[INDEX] = {}

    #                     VILLAGES[INDEX].update({
    #                         # "index": INDEX,
    #                         "district_name": district["district_name_english"],
    #                         "district_code": district["district_code_census"],
    #                         "district_hindi": district["district_name"],

    #                         "tehsil_name": tehsil["tehsil_name_english"],
    #                         "tehsil_code": tehsil["tehsil_code_census"],
    #                         "tehsil_hindi": tehsil["tehsil_name"],

    #                         "village_name": village["vname_eng"],
    #                         "village_code": village["village_code_census"],
    #                         "village_hindi": village["vname"],

    #                         "paragna_hindi": village["pname"],
    #                         "paragna_code": village["pargana_code_new"],

    #                         "flag_survey": 0 if village["flg_survey"] == "N" else 1,
    #                         "flag_chakbandi": 0 if village["flg_chakbandi"] == "N" else 1,

    #                         "flag_ansh": 1
    #                     })

                        
    #         districts = self.__get_data("act=fillDistrictAnshNew", json=True)
    #         for district in districts:
    #             print("RTK: ",district["district_name_english"])
    #             # get all tehsils
    #             tehsils = self.__get_data("act=fillTehsilAnshNew&district_code=" + district["district_code_census"], json=True)
    #             for tehsil in tehsils:
    #                 # get all villages
    #                 villages = self.__get_data("act=fillVillageAnshNew&district_code=" + district["district_code_census"] + "&tehsil_code=" + tehsil["tehsil_code_census"], json=True)
    #                 for village in villages:
    #                     INDEX = "{}/{}/{}".format(district["district_code_census"], tehsil["tehsil_code_census"], village["village_code_census"])
    #                     if INDEX not in VILLAGES:
    #                         VILLAGES[INDEX] = {}

    #                     VILLAGES[INDEX].update({
    #                         # "index": INDEX,
    #                         "district_name": district["district_name_english"],
    #                         "district_code": district["district_code_census"],
    #                         "district_hindi": district["district_name"],

    #                         "tehsil_name": tehsil["tehsil_name_english"],
    #                         "tehsil_code": tehsil["tehsil_code_census"],
    #                         "tehsil_hindi": tehsil["tehsil_name"],

    #                         "village_name": village["vname_eng"],
    #                         "village_code": village["village_code_census"],
    #                         "village_hindi": village["vname"],

    #                         "paragna_hindi": village["pname"],
    #                         "paragna_code": village["pargana_code_new"],

    #                         "flag_survey": 0 if village["flg_survey"] == "N" else 1,
    #                         "flag_chakbandi": 0 if village["flg_chakbandi"] == "N" else 1,

    #                         "flag_rtk": 1
    #                     })

    #         # delete all rows from bhulekhVillages
    #         # with open("bhulekhVillages.json", "w") as f:
    #         #     f.write(json.dumps(VILLAGES, indent=4))

    #         self.__db.query(bhulekhVillages).delete()

    #         # insert all villages
    #         self.__db.add_all([bhulekhVillages(**village) for village in VILLAGES.values()])
    #         self.__db.commit()

    #         lastRorVillageUpdateTime = self.__db.query(configSettings).filter(configSettings.key == "lastRorVillageUpdateTime").first()
    #         lastRorVillageUpdateTime.value = str(datetime.datetime.now().timestamp())
    #         self.__db.commit()

    #         # print("Villages updated successfully")

    #     except Exception as e:
    #         # print("Error while updating villages: ")
    #         # print(e)
    #         self.__db.rollback()
    
    def __get_data(self, url, json=False, html=False):
        if json:
            url = self.__base_url + "action/public_action.jsp?"+url
        else:
            url = self.__base_url + url
        
        print(url)

        response = requests.get(url)
        if json:
            return response.json()
        elif html:
            return response.text
        else:
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup


    def find_between(self,string, start, end, all=False):
        res = []
        arr = string.split(start)
        for k, v in enumerate(arr):
            if k == 0:
                continue
            res.append(v.split(end)[0].strip())
        if all:
            return res
        return res[0]
        