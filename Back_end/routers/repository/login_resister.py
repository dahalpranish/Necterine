from fastapi import Request
from sqlalchemy.orm import Session
from Back_end.core import hashing
from Back_end.models import userdata
from Back_end.schemas import schemas


def get_user_by_email(db:Session,email:str):
    return db.query(userdata.user_data).filter(
        userdata.user_data.user_email == email).first()

def get_user_by_username(db:Session,username:str):
    return db.query(userdata.user_data).filter(
        userdata.user_data.user_name == username).first()

def get_user_by_identifier(db:Session,identifier:str):
    return db.query(userdata.user_data).filter(
        (userdata.user_data.user_name == identifier) | 
        (userdata.user_data.user_email == identifier )
        ).first()
#this is for the user name access for the profile
def get_user_by_id(db:Session,user_id: int):
    return db.query(userdata.user_data).filter(userdata.user_data.uid == user_id).first()

def create_user(db: Session, request: schemas.user_data):
    """Create and persist a new user record."""
    user = userdata.user_data(
        user_name=request.user_name,
        user_email=request.user_email,
        password=hashing.hash(request.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

