from deta import Deta  # Import Deta's SDK

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
    
    def aadhaar_originalsFetch(self):
        all_data = []
        last = None
        while True:
            data = self.aadhaar_originals.fetch(last=last, limit=10000)
            for item in data.items: all_data.append(item)
            if data.last is None: break
            last = data.last
        return all_data

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