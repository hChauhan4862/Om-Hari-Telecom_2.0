import time
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
import uvicorn

from routes.api import router as api_router
from swagger_ui import router as swagger_ui_router
from hcResponseBase import hcCustomException

from db import deta_obj
from utils import router as token_router
import os

app = FastAPI(
    title="Om Hari Telecom- API", 
    version="V1",
    # swagger_ui_parameters={"defaultModelsExpandDepth": -1, "persistAuthorization": True},
    responses={200:{}},
    # openapi_url=None,
    docs_url=None
)

@app.exception_handler(hcCustomException)
async def unicorn_exception_handler(request: Request, exc: hcCustomException):
    if exc.detail == "" and exc.status_code in [401,403,422,429]:
        return HTMLResponse(status_code=exc.status_code, content="")

    return JSONResponse(
        status_code=exc.status_code,
        content={"error": True, "error_code": exc.error_code, "detail": exc.detail, "data" : exc.data},
        headers=exc.headers
    )

@app.exception_handler(Exception)
async def handle_exceptions(request, exc):
    error_msg = {"error": True, "error_code": 500 , "detail" : str(exc), "data" : {}}
    return JSONResponse(error_msg, status_code=status.HTTP_400_BAD_REQUEST)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    # print(exc.errors())
    try:
        variable = exc.errors()[0]["loc"][1]
    except Exception as e:
        variable = ""
    error_msg = {"error": True, "error_code": 422 , "detail" : "Invalid value for "+ variable, "data" : {}}
    return JSONResponse(error_msg, status_code=status.HTTP_400_BAD_REQUEST)

# Middle Ware for all Routes
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000","*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base routes
@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse("favicon.ico")

@app.get("/api", include_in_schema=False)
async def read_root():
    # Create tmp folder if not exists for storing temp files
    if not os.path.exists("/tmp"):
        os.makedirs("/tmp")
    if not os.path.exists("/tmp/epic"):
        os.makedirs("/tmp/epic")
    if not os.path.exists("/tmp/aadhaar"):
        os.makedirs("/tmp/aadhaar")
    
    adminUser = deta_obj.db.authInfo.get("hChauhan")
    userUser = deta_obj.db.authInfo.get("lakhan")

    if adminUser is None:
        from utils import get_password_hash
        deta_obj.db.authInfo.put(
            {
                "uid": 1,
                "name": "H Chauhan",
                "username": "hChauhan",
                "key": "hChauhan",
                "password": get_password_hash("Hps@123"),
                "userRole": "ADMIN",
                "userStatus": True,
                "token_secret" : None,
                "login_at" : None,
                "lastActive_at" : None,
            }
        )
    if userUser is None:
        from utils import get_password_hash
        deta_obj.db.authInfo.put({
                "uid": 2,
                "name": "Lakhan Chauhan",
                "username": "lakhan",
                "key": "lakhan",
                "password": get_password_hash("lakhan"),
                "userRole": "USER",
                "userStatus": True,
                "token_secret" : None,
                "login_at" : None,
                "lastActive_at" : None,
        })

    return {"apiStatus": "live"}

app.include_router(token_router)
app.include_router(api_router)
app.include_router(swagger_ui_router)

if __name__ == '__main__':
    uvicorn.run("main:app", host='0.0.0.0', port=8000, log_level="info", reload=True, server_header=False)