from Back_end.database.base import Base
from datetime import datetime
from sqlalchemy import Column, Integer, String,DateTime,Numeric,Enum
from sqlalchemy.orm import relationship
from Back_end.schemas.dashboard import CategoryEnum

class Category(Base):
    __tablename__ = "Category_table"
    cid= Column( Integer, primary_key=True, index=True)
    category= Column(Enum(CategoryEnum), nullable= False)
    expenses= relationship("Expense",back_populates="category")