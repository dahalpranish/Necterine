from fastapi import APIRouter,Depends,HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from Back_end.schemas import schemas
from Back_end.models import userdata
from Back_end.core import token,hashing
from Back_end.database.database import get_db
from Back_end.core.oauth2 import get_current_user


router= APIRouter("/dashboard")

@router.post("/entry")
def data_entry(db: Session = Depends(get_db)):
    pass

@router.get("/recent")
def recent_entry(db: Session = Depends(get_db)):
    pass