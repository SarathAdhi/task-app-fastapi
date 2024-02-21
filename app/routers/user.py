from fastapi import APIRouter, Depends, HTTPException, status
from ..database.database import get_db
from ..database import models
from ..schemas import schemas
from ..controllers import utils, JWTauth
from sqlalchemy.orm import Session



router = APIRouter(
    prefix='/api/users',
    tags=['Users']
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(models.User).filter(models.User.email == user.email).first()

    if not existing_user:
        user.password = utils.hash(user.password)

        new_user = models.User(**user.model_dump())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"data": new_user, "message": "User Successfully Created"}

    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User with email: {user.email} already exists")
    

@router.get("/{id}", response_model = schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {id} does not exist")
    
    return user


@router.put("/", response_model=schemas.UserOut)
def update_user_info(user_details: schemas.UserUpdate, db: Session = Depends(get_db), current_user: int = Depends(JWTauth.get_current_user)):

    user_query = db.query(models.User).filter(models.User.id == current_user.id)

    if not user_query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")
    
    user_details.password = utils.hash(user_details.password)
    
    user_query.update(user_details.model_dump(), synchronize_session=False)
    db.commit()

    return user_query.first()