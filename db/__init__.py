from deta import Deta  # Import Deta's SDK
from datetime import datetime

# Initialize with a Project Key
deta = Deta("c0why24efad_vTbykfd4RGB5u5wizvhEUbb9vDqWy6Yo")

class DBObj(object):
    def __init__(self):
        self.aadhaar_originals = deta.Base("aadhaar_originals")
        self.authInfo          = deta.Base("authInfo")
        self.configSettings    = deta.Base("configSettings")
        self.ror_districts     = deta.Base("ror_districts")
        self.ror_tehsils       = deta.Base("ror_tehsils")
        self.ror_villages      = deta.Base("ror_villages")
    
    def aadhaar_originalsFetch(self, key = None, UID = None):
        all_data = []
        last = None
        while True:
            q = {}
            if key: q["key"] = key
            if UID: q["UID"] = UID
            data = self.aadhaar_originals.fetch(q, last=last, limit=10000)
            for item in data.items: all_data.append(item)
            if data.last is None: break
            last = data.last
        # sort all_data by addTime
        all_data.sort(key = lambda x: datetime.fromisoformat(x["addTime"]))
        return all_data
    
    def ror_villagesLists(self, village_code = None, village_name = ""):
        if village_code:
            villages = self.ror_villages.fetch({"key": str(village_code)})
        else:
            villages = self.ror_villages.fetch({"village_name?contains": village_name})

        if villages.count == 0: return []
        villages = list(villages.items)
        # sort villages by length of village_name min to max
        villages.sort(key = lambda x: len(x["village_name"]))

        tehsils = self.ror_tehsils.fetch().items
        districts = self.ror_districts.fetch().items

        villages_list = []
        for village in villages:
            tehsil = next((x for x in tehsils if x["tehsil_code"] == village["tehsil_code"]), None)
            district = next((x for x in districts if x["district_code"] == tehsil["district_code"]), None)
            villages_list.append({
                "village_code"  : village["key"],
                "district_name" : district["district_name"] if district and "district_name" in district else None,
                "district_code" : district["key"]           if district else None,
                "district_hindi": district["district_hindi"] if district and "district_hindi" in district else None,
                "tehsil_name"   : tehsil["tehsil_name"]     if tehsil and "tehsil_name" in tehsil else None,
                "tehsil_code"   : tehsil["key"]             if tehsil else None,
                "tehsil_hindi"  : tehsil["tehsil_hindi"]    if tehsil and "tehsil_hindi" in tehsil else None,
                "village_name"  : village["village_name"]   if "village_name" in village else None,
                "village_hindi" : village["village_hindi"]  if "village_hindi" in village else None,
                "paragna_hindi" : village["paragna_hindi"]  if "paragna_hindi" in village else None,
                "paragna_code"  : village["paragna_code"]   if "paragna_code" in village else None,
                "flag_khatauni" : village["flag_khatauni"]  if "flag_khatauni" in village else None,
                "flag_ansh"     : village["flag_ansh"]      if "flag_ansh" in village else None,
                "flag_rtk"      : village["flag_rtk"]       if "flag_rtk" in village else None,
            })
        return villages_list

class FileObj(object):
    def __init__(self):
        self.aadhaar_originals = deta.Drive("aadhaar_originals")

    def aadhaar_originalsList(self):
        all_files = []
        last = None
        while True:
            files = self.aadhaar_originals.list(last=last)
            for file in files["names"]: all_files.append(file)
            if not "paging" in files or not "last" in files["paging"]: break
            last = files["paging"]["last"]
        return all_files

class DetaObj(object):
    def __init__(self):
        self.db = DBObj()
        self.files = FileObj()

############# Usage #############
deta_obj = DetaObj()
