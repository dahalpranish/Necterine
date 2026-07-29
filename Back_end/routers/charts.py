from sqlalchemy import extract
from fastapi import APIRouter,Depends, params,status
from sqlalchemy.orm import Session
from Back_end.models import Expense,Category
from Back_end.database.database import get_db
from Back_end.core.oauth2 import get_current_user
from datetime import date, timedelta,datetime
from Back_end.schemas.charts import *
from Back_end.routers.services.chart_services import *
from collections import defaultdict
from Back_end.routers.repository.chart_repository import chart_comparision

router = APIRouter()

@router.get("/analytics/monthly-summary")
def chart_data(params: CharQueryParams = Depends(), db: Session = Depends(get_db), current_user_token = Depends(get_current_user)):
    rows = chart_comparision(params, db, current_user_token)
    result = monthly_summary(rows,params)
    return result

@router.get("/analytics/category-summary")
def chart_data(params: CharQueryParams = Depends(), db: Session = Depends(get_db), current_user_token = Depends(get_current_user)):
    rows = chart_comparision(params, db, current_user_token)
    result = category_summary(rows,params)
    return result

@router.get("/analytics/category-breakdown")
def chart_data(params: CharQueryParams = Depends(), db: Session = Depends(get_db), current_user_token = Depends(get_current_user)):
    rows = chart_comparision(params, db, current_user_token)
    result = category_breakdown(rows,params)
    return result