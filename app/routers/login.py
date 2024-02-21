from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..database import models
from ..controllers import utils, JWTauth
from ..schemas import schemas
from fastapi.security.oauth2 import OAuth2PasswordRequestForm


router = APIRouter(
    prefix='/api/auth',
    tags = ['Authentication'],
)


@router.post('/login', response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    
    access_token = JWTauth.create_access_token(data={"user_id": user.id})
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get('/verify', response_model=schemas.JWTVerifyResponse, status_code=status.HTTP_200_OK)
def verify_JWT(current_user: int = Depends(JWTauth.get_current_user)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"JWT Expired")
    
    return {"data": current_user, "message": "JWT Verified"}



    

