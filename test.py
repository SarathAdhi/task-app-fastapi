from datetime import datetime, timedelta, timezone
import time
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.database import  engine
from app.database import models


db = Session(bind=engine)


def query_deleted_and_check():
    tasks = db.query(models.Task).filter(models.Task.is_deleted == True).all()

    for task in tasks:
        deleted_at = getattr(task, "deleted_at", None)
        if deleted_at:

            current_time = datetime.now(timezone.utc)
            
            time_threshold = deleted_at + timedelta(days=30)


            if time_threshold <= current_time:
                db.delete(task)
                db.commit()
                print("deleted task")



while True:
    query_deleted_and_check()
    time.sleep(5)
