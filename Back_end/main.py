from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from Back_end.database.database import engine
from Back_end.database.base import Base

from Back_end.routers import login_register

app = FastAPI()

app.include_router(login_register.router)
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)