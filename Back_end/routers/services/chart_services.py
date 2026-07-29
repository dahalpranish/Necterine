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

def monthly_summary(rows,params: CharQueryParams):
    if params.range == RangeEnum.WEEK:
        # No aggregation — every expense is its own point on the graph.
        # Ordered by id (insertion order), NOT by date.
        sorted_rows = sorted(rows, key=lambda r: r[0].eid)

        labels = [exp.date.strftime("%d %b '%y") for exp, cat in sorted_rows]
        totals = [float(exp.amount) for exp, cat in sorted_rows]

    else:
        # MONTH, HALF_YEAR, YEAR, ALL — grouped by exact day (summed),
        # sorted chronologically. Can't sort by id here since several
        # expenses with different ids collapse into one day's total.
        daily = defaultdict(float)
        for exp, cat in rows:
            daily[exp.date] += float(exp.amount)

        sorted_dates = sorted(daily.keys())
        labels = [d.strftime("%d %b '%y") for d in sorted_dates]
        totals = [daily[d] for d in sorted_dates]

    return {
            "labels": labels,
            "totals": totals
        }

def category_summary(rows,params: CharQueryParams):
    monthly = defaultdict(float)
    data_list = []
    for exp, cat in rows:
        key = cat.category
        monthly[key] += float(exp.amount)
    sorted_keys = dict(sorted(monthly.items(), key=lambda item: item[1], reverse=True))
    for key,vlaue in sorted_keys.items():
         data_list.append({"category": key,"total": vlaue})
         
    return data_list

def category_breakdown(rows,params : CharQueryParams):
    if not params.range:
        return {"labels": [], "datasets": []}

    date_fmt = "%d %b" if params.range in (RangeEnum.WEEK, RangeEnum.MONTH) else "%b %Y"

    # 1. Sum amounts per (label, category) — single flat lookup, no nested lists
    totals = defaultdict(float)
    labels_seen = set()
    categories_seen = set()

    for exp, cat in rows:
        label = exp.date.strftime(date_fmt)
        totals[(label, cat.category)] += float(exp.amount)
        labels_seen.add(label)
        categories_seen.add(cat.category)

    # 2. Sort labels chronologically
    sorted_labels = sorted(labels_seen, key=lambda d: datetime.strptime(d, date_fmt))

    # 3. Build datasets — iterate FULL label list per category, fill 0 where missing
    datasets = [
        {
            "category": category,
            "data": [totals.get((label, category), 0) for label in sorted_labels]
        }
        for category in sorted(categories_seen)
    ]

    return {
        "labels": sorted_labels,
        "datasets": datasets
    }    