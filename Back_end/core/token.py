from datetime import datetime,timedelta
from jose import JWTError,jwt
from fastapi import Response
from pydantic import ValidationError
from Back_end.schemas import schemas
import os
from dotenv import load_dotenv
load_dotenv('Back_end/.env')
SECRET_KEY= os.getenv("SECRET_KEY")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 1             # normal session (not "remember me")
REMEMBER_ME_EXPIRE_DAYS = 30   

REFRESH_COOKIE_NAME = "refresh_token"

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict,remember_me:bool = False):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days= REMEMBER_ME_EXPIRE_DAYS if remember_me else REFRESH_TOKEN_EXPIRE_DAYS) 
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token:str,credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=user_id)
        return token_data
    except (JWTError, ValidationError):
        raise credentials_exception

def verify_refresh_token(token:str,credentials_exception):
    try:
        payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=user_id)
        return token_data
    except (JWTError, ValidationError):
        raise credentials_exception


def set_refresh_cookie(response: Response, refresh_token: str, remember_me: bool):
    days = REMEMBER_ME_EXPIRE_DAYS if remember_me else REFRESH_TOKEN_EXPIRE_DAYS
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,       # not accessible to JS — mitigates XSS token theft
        secure=False,         # only sent over HTTPS (use False only in local dev over http)
        samesite=None,      # CSRF mitigation; use "strict" for tighter security
        max_age=days * 24 * 60 * 60,
        path="/",             # scope cookie to whole app (or narrow to /refresh, /logout)
    )