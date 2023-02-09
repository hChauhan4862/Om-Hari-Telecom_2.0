from fastapi import APIRouter, Form, Security
from datetime import datetime, timedelta
from typing import Union

from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm , SecurityScopes
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from hcResponseBase import MeObj, hcCustomException, Me
import uuid

from db import *
from config import *

# openssl rand -hex 32

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token_issue")

class TokenData(BaseModel):
    loginkey: Union[str, None] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

def random():
    return uuid.uuid1().hex[0:16]+uuid.uuid4().hex[0:16]

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = hcCustomException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        # detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        loginkey: str = payload.get("sub")
        if loginkey is None:
            raise credentials_exception
        token_data = TokenData(loginkey=loginkey)
    except JWTError:
        raise credentials_exception
    user = db.query(authInfo).filter(authInfo.token_secret == token_data.loginkey, authInfo.userStatus == True).first()
    if user is None:
        raise credentials_exception
    if security_scopes.scopes:
        if security_scopes.scopes[0] == ":ADMIN:":
            if user.userRole != "ADMIN":
                raise hcCustomException(status_code=403,headers={"WWW-Authenticate": "Bearer"},detail="You are not allowed to access this resource")

    db.query(authInfo).filter_by(token_secret=token_data.loginkey).update(dict(lastActive_at=datetime.datetime.utcnow()))
    db.commit()
    db.refresh(user)
    return MeObj(uid=user.uid,role=user.userRole,username=user.username, db=db)

router = APIRouter(
    prefix="/api/auth",
    tags=["Authorisation"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Incorrect username or password"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {},
        status.HTTP_429_TOO_MANY_REQUESTS: {},
    }
)

@router.post("/token_issue", responses={status.HTTP_200_OK: {"description": "Successful Response", "model": TokenResponse}})
async def token_generate(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    credentials_exception = hcCustomException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user = db.query(authInfo).filter(authInfo.username == form_data.username, authInfo.userStatus == True).first()
    
    # raise credentials_exception
    if user is None or not verify_password(form_data.password, user.password):
        raise credentials_exception

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # 365 days
    key = str(user.uid) + random()

    access_token = create_access_token(
        data={"sub": key}, expires_delta=access_token_expires
    )
    db.query(authInfo).filter_by(uid=user.uid).update(dict(token_secret=key, login_at=datetime.datetime.utcnow()))
    db.commit()
    return {"access_token": access_token, "token_type": "bearer", "expires_in": access_token_expires.total_seconds()}