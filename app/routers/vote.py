from fastapi import Body, Response, status, HTTPException, Depends, APIRouter
from app import oauth2
from .. import models, schemas, utils
from .. database import engine, get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/vote", tags=["Vote"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def vote(vote: schemas.Vote, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {vote.post_id} does not exist.")

    vote_query = db.query(models.Vote).filter(
        models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id)
    found_vote = vote_query.first()

    if found_vote and vote.dir == 1:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"user {current_user.id} has already voted on post {vote.post_id}")
    elif not found_vote and vote.dir == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user {current_user.id} has not voted on post {vote.post_id}")

    message = {"message": "Invalid dir, provide either 1 to vote or 0 to remove vote"}  # default message in case of unexpected behavior
    if vote.dir == 1:
        new_vote = models.Vote(post_id=vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        message=  {"message": "Successfully added vote"}

    if vote.dir == 0:
        vote_query.delete(synchronize_session=False)
        db.commit()
        message=  {"message": "Successfully deleted vote"}

    return message