from fastapi import Body, Response, status, HTTPException, Depends, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from .. import models, schemas, utils, oauth2
from .. database import engine, get_db
from sqlalchemy.orm import Session

router = APIRouter(tags=["Authentication"])


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.email == credentials.username).first()

    if not user or not utils.verify(credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User not found")

    access_token = oauth2.create_access_token(data={"user_id": user.id})

    return {"access_token": access_token, "token_type": "bearer"}
 