from pydantic import BaseModel, EmailStr, Field

class user_data(BaseModel):
    user_name : str
    user_email : EmailStr
    password : str =Field(max_length=72)

class user_login(BaseModel):
    identifier : str
    password : str

class TokenData(BaseModel):
    id: int | None = None  