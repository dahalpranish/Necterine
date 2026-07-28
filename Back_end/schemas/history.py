from enum import Enum
from datetime import date
from typing import Optional
from fastapi import Query

class CategoryEnum(str,Enum):
    ALL = "all"
    FOOD = "Food"
    TRANSPORT = "Transport"
    HOUSING = "Housing"
    HEALTH = "Health"
    ENTERTAINMENT = "Entertainment"
    SHOPPING = "Shopping"
    EDUCATION = "Education"
    OTHER = "Other"

class DateFilterEnum(str,Enum):
    ALL = "all"
    TODAY = "today"
    YESTERDAY = "yesterday"
    WEEK = "week"
    MONTH = "month"
    CUSTOM = "custom"

class SortEnum(str,Enum):
    DATE_DESC = "date_desc"
    DATE_ASC = "date_asc"
    AMOUNT_DEFAULT = "amount_default"
    AMOUNT_ASC = "amount_asc"
    AMOUNT_DESC = "amount_desc"

class ExpenseQueryParams:
    def __init__(
        self,
        search: Optional[str] = Query(default=None),
        category: CategoryEnum = Query(default=CategoryEnum.ALL),
        date_filter: DateFilterEnum = Query(default=DateFilterEnum.ALL),
        start_date: Optional[date] = Query(default=None),
        end_date: Optional[date] = Query(default=None),
        sort: SortEnum = Query(default=SortEnum.DATE_DESC),
    ):
        self.search = search
        self.category = category
        self.date_filter = date_filter
        self.start_date = start_date
        self.end_date = end_date
        self.sort = sort
