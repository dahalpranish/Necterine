from pydantic import AliasPath, BaseModel, Field,ConfigDict,Field
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
    price: float = Field(validation_alias="amount")
    id:int = Field(validation_alias="eid")
    category: CategoryEnum = Field(validation_alias=AliasPath("category", "category"))

    model_config = ConfigDict(from_attributes=True,populate_by_name=True)

class analytic(BaseModel):
    this_month_total : float
    last_month_total: float
    this_month_count : int
    top_category : str
    percent_change_vs_last_month: float
