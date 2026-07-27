from pydantic import BaseModel,field_serializer,ConfigDict
from datetime import date,datetime
from enum import Enum
class CategoryEnum(str,Enum):
    FOOD = "Food"
    TRANSPORT = "Transport"
    HOUSING = "Housing"
    HEALTH = "Health"
    ENTERTAINMENT = "Entertainment"
    SHOPPING = "Shopping"
    EDUCATION = "Education"
    OTHER = "Other"
class expense_write(BaseModel):
    date: date
    description : str
    category: CategoryEnum
    price : float
class expense_show(expense_write):
    eid:int
    created_at:datetime
    @field_serializer('created_at')
    def serialize_date_only(self, dt: datetime, _info):
        return dt.strftime("%d %b %Y")

    model_config = ConfigDict(from_attributes=True)
