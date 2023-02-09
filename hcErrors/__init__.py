from xmlrpc.client import boolean
from fastapi import Body
from pydantic import BaseModel

class ValidationError(BaseModel):
    error: boolean = Body(title="Always true")
    detail : str = Body(title="Error Description",example="Validation Error")
    variable : str

class hcCustomError(BaseModel):
    error: boolean = Body(title="Always true")
    detail : str = Body(title="Error Description",example="Validation Error")
    error_code : int = Body(title="Error Code",example=400)

class hcCustomException(Exception):
    def __init__(self, status_code: int = 400, detail: str = "SomeThing Went Wrong", error_code: int = 400):
        self.detail = detail
        self.status_code = status_code
        self.error_code = error_code

