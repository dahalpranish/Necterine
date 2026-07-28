from Back_end.schemas.charts import RangeEnum,CharQueryParams
from Back_end.models import Expense,Category
from datetime import date,timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session
from collections import defaultdict


def chart_comparision(params:CharQueryParams,db:Session,current_user_token):
    query= db.query(Expense,Category).join(Category,Expense.category_id==Category.cid).filter(Expense.user_id == current_user_token.id)
    if params.range:
        if params.range == RangeEnum.WEEK:
            query = query.filter(Expense.date>= date.today()-timedelta(days=7))
        elif params.range == RangeEnum.MONTH:
            query = query.filter(Expense.date > date.today()-relativedelta(months=1) )
        elif params.range == RangeEnum.HALF_YEAR:
            query = query.filter(Expense.date > date.today()-relativedelta(months=6) )
        elif params.range == RangeEnum.YEAR:
            query = query.filter(Expense.date > date.today()-relativedelta(months=12) )

    return query.all()