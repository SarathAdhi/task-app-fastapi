from fastapi import APIRouter, Depends, HTTPException, status, Query
from ..database.database import get_db
from ..database import models
from ..schemas import schemas
from ..controllers import JWTauth
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from sqlalchemy import desc


router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


@router.get("/", response_model=schemas.TaskOutResponse)
def get_user_tasks(
    priority: schemas.PriorityEnum = Query(None),
    completed: bool = Query(None),
    dline_passed: bool = Query(None),
    search: Optional[str] = "",
    sort: schemas.SortEnum = Query(None),
    deleted: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: int = Depends(JWTauth.get_current_user),
):

    query = (
        db.query(models.Task)
        .filter(
            models.Task.owner_id == current_user.id,
            models.Task.content.contains(search),
        )
        .order_by(desc(models.Task.created_at))
    )

    if completed is not None:
        query = query.filter(models.Task.completed == completed)

    if dline_passed is not None:
        if dline_passed:
            query = query.filter(models.Task.deadline < datetime.utcnow())

        else:
            query = query.filter(models.Task.deadline > datetime.utcnow())

    if priority is not None:
        query = query.filter(models.Task.priority == priority)

    if deleted is not None:
        if deleted == "true":
            query = query.filter(models.Task.is_deleted == True)
        elif deleted == "false":
            query = query.filter(models.Task.is_deleted == False)
    else:
        query = query.filter(models.Task.is_deleted == False)

    if sort is not None:
        if sort == "earliest":
            query = query.order_by(models.Task.created_at)
        else:
            query = query.order_by(models.Task.created_at.desc())

    tasks = query.all()

    return {"data": tasks}


@router.get("/{id}", response_model=schemas.TaskOut)
def get_user_task_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(JWTauth.get_current_user),
):

    task = (
        db.query(models.Task)
        .filter(models.Task.id == id, models.Task.owner_id == current_user.id)
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id: {id} does not exist",
        )

    return task


@router.post("/", response_model=schemas.TaskResponse)
def create_task(
    task: schemas.Task,
    db: Session = Depends(get_db),
    current_user: int = Depends(JWTauth.get_current_user),
):

    new_task = models.Task(owner_id=current_user.id, **task.model_dump())
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return {"data": new_task}


@router.put("/{id}", response_model=schemas.TaskResponse)
def update_task(
    id: int,
    task: schemas.Task,
    db: Session = Depends(get_db),
    current_user: int = Depends(JWTauth.get_current_user),
):

    task_query = db.query(models.Task).filter(models.Task.id == id)
    task_exist = task_query.first()

    if not task_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id: {id} does not exist",
        )

    if task_exist.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorised to perform requested action",
        )

    task_query.update(task.model_dump(), synchronize_session=False)
    db.commit()

    task = task_query.first()

    return {"data": task}


@router.delete("/{id}", response_model=schemas.TaskDeleteOutResponse)
def delete_task(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(JWTauth.get_current_user),
):

    task_query = db.query(models.Task).filter(models.Task.id == id)
    task = task_query.first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id: {id} does not exist",
        )

    if task.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorised to perform requested action",
        )

    if task.is_deleted:
        db.delete(task)
        db.commit()

        return {"data": task, "message": "Task deleted permanently"}

    task_query.update(
        {models.Task.is_deleted: True, models.Task.deleted_at: datetime.now()}
    )
    db.commit()

    return {"data": task, "message": "Task moved to trash"}


@router.put("/restore/{id}", response_model=schemas.TaskOut)
def restore_deleted_task(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(JWTauth.get_current_user),
):

    task_query = db.query(models.Task).filter(models.Task.id == id)
    task = task_query.first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id: {id} does not exist",
        )

    if task.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorised to perform requested action",
        )

    task_query.update({models.Task.is_deleted: False, models.Task.deleted_at: None})
    db.commit()

    return task_query.first()
