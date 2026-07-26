from fastapi import APIRouter,Depends,HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from Back_end.schemas import schemas
from Back_end.models import userdata
from Back_end.core import token,hashing
from database import get_db



router = APIRouter(prefix="/user")



@router.post("/resister",tags=[ "Register"],response_model=status.HTTP_200_OK)
def resister(request:schemas.user_data,db: Session = Depends(get_db)):
    existing_email = db.query(userdata.user_data).filter(userdata.user_data.email == request.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")
    existing_username = db.query(userdata.user_data).filter(userdata.user_data.username == request.username).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="username already exists")
    user = userdata.user_data(username = request.username, email = request.email, password = hashing.hash(request.password))
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"username": user.username, "email":user.email,"password":user.password}

@router.post("/login", tags=["login_authentication"],response_model= status.HTTP_200_OK)
def login(request: schemas.user_login, db: Session = Depends(get_db)):
    user = db.query(userdata.user_data).filter(
        (userdata.user_data.username == request.identifier) |
        (userdata.user_data.email == request.identifier)
    ).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incorrect username ")

    if not hashing.verify(user.password, request.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")

    access_token = token.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}