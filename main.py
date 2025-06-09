from fastapi import FastAPI
from database import engine, Base

Base.metadata.create_all(bind=engine)

import user_routes
import root_routes

app = FastAPI()

app.include_router(root_routes.router)
app.include_router(user_routes.router)





