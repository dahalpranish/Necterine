from Back_end.database.base import Base
from datetime import datetime,timezone
from sqlalchemy import Column, Integer, String,DateTime,Numeric,ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Expense(Base):
    __tablename__ = "Expense_table"
    eid= Column( Integer, primary_key=True, index=True)
    description= Column(String, nullable= False)
    time = Column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    amount = Column(Numeric(precision=10,scale=2),nullable=False)
    category_id= Column(String,ForeignKey("Category_table.cid"),nullable=False)
    user_id = Column(String,ForeignKey("userdata.uid"),nullable=False)
    user= relationship("user_data",back_populates="expenses")
    category= relationship("Category",back_populates="expenses")

