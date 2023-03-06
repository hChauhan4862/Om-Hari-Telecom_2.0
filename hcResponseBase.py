from typing import Any, Callable, Optional, Sequence, Union, List
from fastapi import Body, params
from pydantic import BaseModel

# class Token(BaseModel):
#     access_token: str
#     token_type: str

def Security(dependency: Optional[Callable[..., Any]] = None,*,scopes: Optional[Union[Sequence[int],Sequence[str]]] = None,use_cache: bool = True):
    if scopes and len(scopes) > 0 and type(scopes[0]) == int:
        for i in range(len(scopes)):
            scopes[i] = str(scopes[i])
    return params.Security(dependency=dependency, scopes=scopes, use_cache=use_cache)

class hcCustomError(BaseModel):
    error: bool = Body(default=True)
    error_code : int = Body(default=400)
    detail : str = Body(default="Error Description")
    data : dict = Body(example={})

class hcCustomException(Exception):
    def __init__(self, status_code: int = 400, detail: str = "", error_code: int = -1, headers: dict = None):
        self.detail = detail
        self.status_code = status_code
        self.error_code = error_code if error_code != -1 else status_code
        self.headers = headers
        self.data = {}

class hcSuccessModal(BaseModel):
    error: int = Body( example=False, default=False)
    error_code: int = Body( example=200, default=200)
    detail : str = Body(default="Success")
    # data: list = list[dataClass]

class Me(BaseModel):
    uid: int
    username: str
    role: str
    
    class Config:
        arbitrary_types_allowed = True

class MeObj(object):
    def __init__(self, username, uid,role):
        self.username = username
        self.uid = uid
        self.role = role

class hcRes(object):
    def __init__(self, error: bool = False, error_code: int = 200, detail: str = "Success", data: dict = {}):
        self.error = error
        self.error_code = error_code
        self.detail = detail
        self.data = data

# class hcSuccessModal2(hcSuccessModal):
#     class dataClass(BaseModel):
#         msg: int = Body( description="Always False")
#     data: List[dataClass]

# class userResponse(hcSuccessModal):
#     class dataClass(BaseModel):
#         msg: str = Body( description="Always False")
#     data: List[dataClass]
#     pass