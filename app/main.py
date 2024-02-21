from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import user, task, login
from .database.database import engine
from .controllers import task_deleter
import time


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(task.router)
app.include_router(login.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


# while True:
#     task_deleter.query_deleted_and_check()
#     time.sleep(5)

