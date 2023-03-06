from fastapi import APIRouter, Request
from typing import List, Optional
from fastapi import Query, Path, Body
from fastapi.responses import FileResponse, StreamingResponse

from io import BytesIO

from utils import get_current_user, Security
from hcResponseBase import hcSuccessModal, hcCustomException, Me, hcRes, MeObj
from db import deta_obj
from utils import get_password_hash
from config import *