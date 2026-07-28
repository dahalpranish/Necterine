from enum import Enum
from fastapi import Query
class RangeEnum(str,Enum):
    # range=week|month|half_year|year|all
    WEEK = "week"
    MONTH = "month"
    HALF_YEAR = "half_year"
    YEAR = "year"
    ALL = "all"

class CharQueryParams:
    def __init__(self, range: RangeEnum = Query(default=RangeEnum.ALL)):
        self.range = range