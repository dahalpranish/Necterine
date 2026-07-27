from sys import prefix

from fastapi import APIRouter,Depends,HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from Back_end.schemas import dashboard
from Back_end.models import Expense,Category
from Back_end.core import token,hashing
from Back_end.database.database import get_db
from Back_end.core.oauth2 import get_current_user
from datetime import datetime
from Back_end.schemas import dashboard
from decimal import Decimal


router= APIRouter()

@router.post("/expenses")
def data_entry(request:dashboard.expense_write,
               db: Session = Depends(get_db),current_user_token = Depends(get_current_user)):
    category_verify= db.query(Category).filter(Category.category == request.category).first()
    expense_entry = Expense(description=request.description,
                                    date= request.date,
                                    category_id = category_verify.cid,
                                    amount = request.price,
                                    user_id = current_user_token.id )
    if  expense_entry.amount < 1 :
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,detail="amount must be greater than zero")
    elif not expense_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="something went wrong!!")
    db.add(expense_entry)
    db.commit()
    db.refresh(expense_entry)
    return True
    

@router.get("/recent")
def recent_entry(db: Session = Depends(get_db)):
    pass