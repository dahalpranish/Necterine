from fastapi import APIRouter,Depends,HTTPException,status,Response
from sqlalchemy.orm import Session
from Back_end.schemas import schemas
from Back_end.core import token,hashing
from Back_end.database.database import get_db
from Back_end.core.oauth2 import get_current_user
from Back_end.routers.repository.login_resister import *



router = APIRouter(prefix="/auth")



@router.post("/register",tags=[ "Register"],status_code=status.HTTP_200_OK)
def resister(request:schemas.user_data,db: Session = Depends(get_db)):

    existing_email = get_user_by_email(db,request.user_email)
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")
    existing_username = get_user_by_username(db,request.user_name)
    if existing_username:
        raise HTTPException(status_code=400, detail="username already exists")
    user= create_user(db,request)
    return {"user_name": user.user_name, "user_email":user.user_email}

@router.post("/login", tags=["login_authentication"],status_code= status.HTTP_200_OK)
def login(request: schemas.user_login,response: Response, db: Session = Depends(get_db)):
    user = get_user_by_identifier(db,request.identifier)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incorrect username ")

    if not hashing.verify(user.password, request.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")

    access_token = token.create_access_token(data={"sub": str(user.uid)})
    refresh_token = token.create_refresh_token(data = {"sub": str(user.uid)})
    token.set_refresh_cookie(response,refresh_token,request.remember_me)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", tags=["Register"], status_code=status.HTTP_200_OK)
def read_current_user(current_user_token = Depends(get_current_user), db: Session = Depends(get_db)):
    user = get_user_by_id(db,int(current_user_token.id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"user_name": user.user_name, "user_email": user.user_email}

@router.post("/refresh", status_code=status.HTTP_200_OK,tags=["login_authentication"])
def refresh(request: Request, response: Response, db: Session = Depends(get_db)):
    old_refresh = request.cookies.get(token.REFRESH_COOKIE_NAME)
    if not old_refresh:
        raise HTTPException(status_code=401, detail="No refresh token")
    credentials_exception = HTTPException(status_code=401, detail="Invalid refresh token")

    new_access = token.verify_refresh_token(old_refresh,credentials_exception)
    return {"access_token": new_access, "token_type": "bearer"}