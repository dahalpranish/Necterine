from sqlalchemy import extract
from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session
from Back_end.models import Expense,Category, expense
from Back_end.database.database import get_db
from Back_end.core.oauth2 import get_current_user
from datetime import date, timedelta
from Back_end.schemas import dashboard
from Back_end.schemas.history import *


router = APIRouter()

@router.get("/expenses/")
def history(params: ExpenseQueryParams=Depends(),db: Session = Depends(get_db),current_user_token = Depends(get_current_user)):
    query= db.query(Expense,Category).join(Category,Expense.category_id==Category.cid).filter(Expense.user_id == current_user_token.id)
    if params.search :
        query= query.filter(Expense.description.ilike(f"%{params.search}%"))
    if params.category and params.category != CategoryEnum.ALL :
        query = query.filter(Category.category == params.category.value)# here the value is the FOOD -> food from the categoryEnum and we used join becase the query is the category name but the Expense has only category_id, so to compare category name to query category name we joind the Category and Expense table using join with condition where the primary and foreign key matched category_id == cid
    if params.date_filter and params.date_filter !=DateFilterEnum.ALL:
        if params.date_filter == DateFilterEnum.TODAY:
            query = query.filter(Expense.date == date.today())
        elif params.date_filter == DateFilterEnum.YESTERDAY:
            query = query.filter(Expense.date == (date.today()-timedelta(days=1)))
        elif params.date_filter == DateFilterEnum.WEEK:
            query = query.filter(Expense.date >= (date.today()-timedelta(days=7)))
        elif params.date_filter == DateFilterEnum.MONTH:
            query = query.filter(extract('year',Expense.date) == date.today().year,
                                 extract('month',Expense.date)== date.today().month)
        elif params.date_filter == DateFilterEnum.CUSTOM:
            if params.start_date and params.end_date:
                query = query.filter(Expense.date >= params.start_date, Expense.date <= params.end_date)

    if params.sort:
        if params.sort == SortEnum.DATE_DESC:
            query = query.order_by(Expense.date.desc())
        elif params.sort == SortEnum.DATE_ASC:
            query = query.order_by(Expense.date.asc())
        elif params.sort == SortEnum.AMOUNT_ASC:
            query = query.order_by(Expense.amount.asc())
        elif params.sort == SortEnum.AMOUNT_DESC:
            query = query.order_by(Expense.amount.desc())
        elif params.sort == SortEnum.AMOUNT_DEFAULT:
            query = query.order_by(Expense.eid.desc())

    expense = query.all()
    response = []
    for exp, cat in expense:
        response.append({
            "id": exp.eid,
            "description": exp.description,
            "price": exp.amount,
            "date": exp.date,
            "category": cat.category
        })
    return response


@router.delete("/expenses/{id}")
def delete_expense(id:int,db: Session = Depends(get_db),current_user_token = Depends(get_current_user)):
    delete = db.query(Expense).filter(Expense.eid == id , current_user_token.id == Expense.user_id).first()
    # if not delete:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="the data couldnt be deleted")
    db.delete(delete)
    db.commit()
    return status.HTTP_200_OK

        
        