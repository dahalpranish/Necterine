from fastapi import APIRouter,Depends,HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from Back_end.schemas import schemas
from Back_end.models import userdata
from Back_end.core import token,hashing
from Back_end.database.database import get_db



router = APIRouter(prefix="/auth")



@router.post("/register",tags=[ "Register"],status_code=status.HTTP_200_OK)
def resister(request:schemas.user_data,db: Session = Depends(get_db)):
    existing_email = db.query(userdata.user_data).filter(userdata.user_data.user_email == request.user_email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")
    existing_username = db.query(userdata.user_data).filter(userdata.user_data.user_name == request.user_name).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="username already exists")
    user = userdata.user_data(user_name = request.user_name, user_email = request.user_email, password = hashing.hash(request.password))
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"user_name": user.user_name, "user_email":user.user_email,"password":user.password}

@router.post("/login", tags=["login_authentication"],status_code= status.HTTP_200_OK)
def login(request: schemas.user_login, db: Session = Depends(get_db)):
    user = db.query(userdata.user_data).filter(
        (userdata.user_data.user_name == request.identifier) |
        (userdata.user_data.user_email == request.identifier)
    ).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incorrect username ")

    if not hashing.verify(user.password, request.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")

    access_token = token.create_access_token(data={"sub": str(user.uid)})
    return {"access_token": access_token, "token_type": "bearer"}