from sqlalchemy import extract,func
from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session
from Back_end.schemas import dashboard
from Back_end.models import Expense,Category
from Back_end.database.database import get_db
from Back_end.core.oauth2 import get_current_user
from datetime import date
from Back_end.schemas import dashboard


router= APIRouter()

@router.post("/expenses/")
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
    

@router.get("/expenses/today",response_model=list[dashboard.expense_show])
def recent_entry(db: Session = Depends(get_db),current_user_token = Depends(get_current_user)):
    todays_expense= db.query(Expense).filter(Expense.date == date.today() , Expense.user_id== current_user_token.id).limit(10).all()
    if not todays_expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="no expense found")
    todays_expense = sorted(todays_expense, key=lambda item: item.eid,reverse=True)
    return todays_expense

@router.get("/analytics/summary",response_model=dashboard.analytic)
def analytic(db: Session = Depends(get_db),current_user_token = Depends(get_current_user)):
    this_month= db.query(Expense).filter(extract('month',Expense.date) == date.today().month,
                                            extract('year',Expense.date) == date.today().year,
                                              Expense.user_id== current_user_token.id).all()
    this_month_total = sum(expense.amount for expense in this_month)
    all_time= db.query(Expense).filter(Expense.user_id== current_user_token.id).limit(10).all()
    all_time_total = sum(expense.amount for expense in all_time)
    last_month =db.query(Expense).filter(extract('month',Expense.date) == date.today().month-1,
                                            extract('year',Expense.date) == date.today().year,
                                              Expense.user_id== current_user_token.id).all()
    last_month_total = sum(expense.amount for expense in last_month)
    highest_category= db.query(Expense.category_id).filter(
                                                extract('month',Expense.date) == date.today().   month,
                                                extract('year',Expense.date) == date.today().year,
                                                  Expense.user_id== current_user_token.id).group_by(Expense.category_id).order_by(func.sum(Expense.amount).desc()).limit(1).scalar()
    if last_month_total == 0 and this_month_total >0 :
        percent_change_vs_last_month = 100
    elif last_month_total >0 :
        percent_change_vs_last_month = ((this_month_total-last_month_total)/last_month_total)*100
    if highest_category:
        category = db.query(Category.category).filter(Category.cid==highest_category).scalar()
    else:
        category= None
    # if not this_month_total|all_time_total|last_month_total:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="no expense found")
    return {
"this_month_total": this_month_total,
  "last_month_total": all_time_total,
  "this_month_count": len(this_month),
  "top_category": category,
  "percent_change_vs_last_month": percent_change_vs_last_month
    }