from sqlalchemy import create_engine 
from urllib.parse import quote_plus
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import String,Text, Unicode, UnicodeText, Integer, SmallInteger, BigInteger, Numeric, Float, DateTime, Date, Time
from sqlalchemy import LargeBinary, Enum, Boolean, JSON, ARRAY, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.mysql import LONGTEXT, MEDIUMTEXT, TINYTEXT, TINYINT, MEDIUMINT, BIGINT, DOUBLE, FLOAT, DECIMAL, BIT, BLOB, MEDIUMBLOB, LONGBLOB, YEAR, DATE, TIME, DATETIME, TIMESTAMP, SET, ENUM, INTEGER, VARCHAR, CHAR, TEXT
from sqlalchemy import Column
import platform
import datetime

DATABASE_URL = "mysql+pymysql://OmHariTelecom:%s@localhost:3306/omharitelecom?charset=utf8" % quote_plus("Oht202132")

Base = declarative_base()

class authInfo(Base):
   __tablename__ = 'authInfo'
   uid = Column(Integer,primary_key = True, unique = True, nullable = False, index = True, autoincrement = True)
   name = Column(String(50), nullable = False)
   username = Column(String(50), nullable = False, unique = True)
   password = Column(String(64), nullable = False,)
   token_secret = Column(String(40) , unique = True)
   userRole = Column(String(10), nullable = False)
   userStatus = Column(Boolean, nullable = False, default = True)
   login_at = Column(DateTime)
   lastActive_at = Column(DateTime)
   created_at = Column(DateTime, nullable = False, default = datetime.datetime.utcnow)
   updated_at = Column(DateTime, nullable = False, default = datetime.datetime.utcnow)

class configSettings(Base):
   __tablename__ = 'configSettings'
   key = Column(String(50),primary_key = True, nullable = False, unique = True, index = True)
   value = Column(String(50), nullable = False)

class uid_cards(Base):
   __tablename__ = 'uid_cards'
   uid_no = Column(String(12), primary_key = True, unique = True, nullable = False, index = True)
   name = Column(String(50), nullable = False)
   name_h = Column(String(50), nullable = False)
   dob = Column(String(10), nullable = False)
   gender = Column(String(1), nullable = False)
   co = Column(String(50), nullable = False)
   co_h = Column(String(50), nullable = False)
   pin = Column(Integer, nullable = False)
   add = Column(String(100), nullable = False)
   add_h = Column(String(100), nullable = False)
   po = Column(String(50), nullable = False)
   po_h = Column(String(50), nullable = False)
   dist = Column(String(50), nullable = False)
   dist_h = Column(String(50), nullable = False)
   state = Column(String(50), nullable = False)
   state_h = Column(String(50), nullable = False)
   qr_text = Column(String(100), nullable = False)
   image_data = Column(Text, nullable = False)

class uid_cards_history(Base):
   __tablename__ = 'uid_cards_history'
   id = Column(Integer, primary_key = True, unique = True, nullable = False, index = True, autoincrement = True)
   uid_no = Column(String(12), nullable = False)
   name = Column(String(50), nullable = False)
   name_h = Column(String(50), nullable = False)
   dob = Column(String(10), nullable = False)
   gender = Column(String(1), nullable = False)
   co = Column(String(50), nullable = False)
   co_h = Column(String(50), nullable = False)
   pin = Column(Integer, nullable = False)
   add = Column(String(100), nullable = False)
   add_h = Column(String(100), nullable = False)
   po = Column(String(50), nullable = False)
   po_h = Column(String(50), nullable = False)
   dist = Column(String(50), nullable = False)
   dist_h = Column(String(50), nullable = False)
   state = Column(String(50), nullable = False)
   state_h = Column(String(50), nullable = False)
   qr_text = Column(String(100), nullable = False)
   image_data = Column(Text, nullable = False)
   add_by = Column(Integer, ForeignKey('authInfo.uid'), nullable = False)
   add_time = Column(TIMESTAMP, nullable = False)

class aadhaar_pdf(Base):
   __tablename__ = 'aadhaar_pdf'
   UID = Column(String(12), primary_key = True, unique = True, nullable = False, index = True)
   Name = Column(String(255))
   DOB = Column(Date)
   Gender = Column(String(1))
   Photo = Column(Text(2097152))
   Mobile = Column(String(10))
   CareOf = Column(String(255))
   Locality = Column(String(255))
   VillageTown = Column(String(255))
   PostOffice = Column(String(255))
   District = Column(String(255))
   SubDistrict = Column(String(255))
   State = Column(String(255))
   Address = Column(String(255))
   
   local_language = Column(String(255))
   local_Name = Column(String(255))
   local_CareOf = Column(String(255))
   # local_Locality = Column(String(255))
   # local_VillageTown = Column(String(255))
   # local_PostOffice = Column(String(255))
   # local_District = Column(String(255))
   # local_SubDistrict = Column(String(255))
   # local_State = Column(String(255))
   local_Address = Column(String(255))

   PinCode = Column(String(6))  # pincode
   IssueDate = Column(Date)
   DownloadDate = Column(Date)

class bhulekhVillages(Base):
   __tablename__ = 'bhulekhVillages'
   # index = Column(String(50), unique = True, nullable = False, index = True)
   village_code = Column(String(50), nullable = False, index = True, unique = True, primary_key = True)

   district_name = Column(String(50), nullable = False)
   district_code = Column(String(50), nullable = False)
   district_hindi = Column(String(50), nullable = False)

   tehsil_name = Column(String(50), nullable = False)
   tehsil_code = Column(String(50), nullable = False)
   tehsil_hindi = Column(String(50), nullable = False)

   village_name = Column(String(50), nullable = False)
   village_hindi = Column(String(50), nullable = False)

   paragna_hindi = Column(String(50), nullable = False)
   paragna_code = Column(String(50), nullable = False)

   flag_survey = Column(Boolean, nullable = False)
   flag_chakbandi = Column(Boolean, nullable = False)

   flag_khatauni = Column(Boolean, nullable = False, default = False)
   flag_ansh = Column(Boolean, nullable = False, default = False)
   flag_rtk = Column(Boolean, nullable = False, default = False)
