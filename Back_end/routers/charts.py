from sqlalchemy import extract
from fastapi import APIRouter,Depends,status
from sqlalchemy.orm import Session
from Back_end.models import Expense,Category
from Back_end.database.database import get_db
from Back_end.core.oauth2 import get_current_user
from datetime import date, timedelta
from Back_end.schemas.charts import *
from collections import defaultdict
from Back_end.routers.repository.chart_repository import chart_comparision

router = APIRouter()

@router.get("/analytics/monthly-summary")
def chart_data(params: CharQueryParams = Depends(), db: Session = Depends(get_db), current_user_token = Depends(get_current_user)):
    rows = chart_comparision(params, db, current_user_token)
    monthly = defaultdict(float)
    if params.range:
        if params.range == RangeEnum.WEEK or params.range == RangeEnum.MONTH:
            for exp, cat in rows:
                key = exp.date.strftime("%d %b")
                monthly[key] += float(exp.amount)
                sorted_keys = sorted(monthly.keys())
 # "2026-01" sort correctly as string
        elif params.range == RangeEnum.HALF_YEAR or params.range == RangeEnum.YEAR or params.range == RangeEnum.ALL:
            for exp, cat in rows:
                key = exp.date.strftime("%b %Y")
                monthly[key] += float(exp.amount)
                sorted_keys = sorted(monthly.keys())  # "2026-01" sort correctly as string


    return {
        "labels": sorted_keys,
        "totals": [monthly[k] for k in sorted_keys]
    }
@router.get("/analytics/category-summary")
def chart_data(params: CharQueryParams = Depends(), db: Session = Depends(get_db), current_user_token = Depends(get_current_user)):
    rows = chart_comparision(params, db, current_user_token)
    monthly = defaultdict(float)
    data_list = []
    for exp, cat in rows:
                    key = cat.category
                    monthly[key] += float(exp.amount)
    sorted_keys = dict(sorted(monthly.items(), key=lambda item: item[1], reverse=True))
    for key,vlaue in sorted_keys.items():
         data_list.append({"category": key,"total": vlaue})
         
    return data_list

@router.get("/analytics/category-breakdown")
def chart_data(params: CharQueryParams = Depends(), db: Session = Depends(get_db), current_user_token = Depends(get_current_user)):
    rows = chart_comparision(params, db, current_user_token)
    monthly = defaultdict(list)
    dataset = defaultdict(dict)
    datasets=[]
    if params.range:
        if params.range == RangeEnum.WEEK or params.range == RangeEnum.MONTH:
            for exp, cat in rows:
                main_key =  exp.date.strftime("%d %b")
                key = cat.category
                monthly[key].append(float(exp.amount))
                dataset[main_key] = monthly[key]

        elif params.range == RangeEnum.HALF_YEAR or params.range == RangeEnum.YEAR or params.range == RangeEnum.ALL:
            for exp, cat in rows:
                main_key =  exp.date.strftime("%b %Y")
                key = cat.category
                monthly[key].append(float(exp.amount))
                dataset[main_key] = monthly[key]            
    data_list= list(dataset.keys())

    for sub_dict in dataset.values():
        for category, data in sub_dict.items():
            datasets.append({
            "category": category,
            "data": data
        })
    return {
         "labels": data_list,
         "datasets": datasets
    }