from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.database.database import  engine
from app.database import models
import time


db = Session(bind=engine)


def query_deleted_and_check():
    print("checking")
    tasks = db.query(models.Task).filter(models.Task.is_deleted == True).all()
    print(len(tasks))

    for task in tasks:
        deleted_at = getattr(task, "deleted_at", None)
        if deleted_at:

            current_time = datetime.now(timezone.utc)
            
            time_threshold = deleted_at + timedelta(days=30)


            if time_threshold <= current_time:
                db.delete(task)
                db.commit()


# while True:
#     query_deleted_and_check()
#     time.sleep(5)