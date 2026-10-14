from fastapi import Body, Response, status, HTTPException, Depends, APIRouter
from .. import models, schemas, utils
from .. database import engine, get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Limit password length to 72 characters for bcrypt
    try:
        hashed_password = utils.hash(user.password)
        user.password = hashed_password
        new_user = models.User(**user.model_dump())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"User with email: {user.email} could not be created. Error: {e}")
    return new_user


@router.get("/{id}", response_model=schemas.User)
async def get_user(id: int, db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"User with id: {id} could not be found.")
    return user
