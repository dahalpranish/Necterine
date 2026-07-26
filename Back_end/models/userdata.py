from sqlalchemy import String,Integer,Column
from Back_end.database.base import Base

class user_data(Base):
    __tablename__ = "userdata"
    uid= Column(Integer,primary_key= True, index= True)
    user_name = Column(String,nullable= False)
    user_email = Column(String,nullable= False)
    password = Column(String,nullable= False)
