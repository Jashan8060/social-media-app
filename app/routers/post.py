from fastapi import Body, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy import func
from .. import models, schemas, utils, oauth2
from .. database import engine, get_db
from sqlalchemy.orm import Session
from typing import Optional

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[schemas.PostOut])
async def get_posts(db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    # cursor.execute("""SELECT * FROM posts ORDER BY id""")
    # posts = cursor.fetchall()
    # return {"data": posts}
    # fetch all posts irrespective of the user
    # posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    # include votes in posts
    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return posts


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
async def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    # print(new_post.rating)
    # my_posts.append(new_post.model_dump())
    # response.status_code = status.HTTP_201_CREATED

    # Raw SQL commands using psycopg2
    # cursor.execute("""INSERT INTO posts (title, content) VALUES (%s, %s) RETURNING *""",
    #                (post.title, post.content))
    # new_post = cursor.fetchone()
    # conn.commit()

    # Using SQLAlchemy ORM
    print(current_user.email)
    post_dict = post.model_dump()
    post_dict["user_id"] = current_user.id
    print(post_dict)
    new_post = models.Post(**post_dict)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/{id}", response_model=schemas.PostOut)
async def get_post(id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    # raw SQL commands using psycopg2
    # cursor.execute("""SELECT * FROM posts WHERE id=%s """, (id,))
    # post = cursor.fetchone()

    # Using SQLAlchemy ORM

    # get post with votes count
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).where(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} does not exist or does not belong to the current user")
    return post


@router.delete("/{id}")
async def delete_post(id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    # raw sql commands using psycopg2
    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (id,))
    # deleted_post = cursor.fetchone()
    # conn.commit()

    print(models.Post.user_id)
    # print(current_user.id)
    

    # using sqlalchemy
    post_query = db.query(models.Post).where(
        models.Post.id == id)

    post = post_query.first()

    if not post:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Post with id: {id} could not be found")
    
    if post.user_id != current_user.id: # type: ignore
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Not authorized to perform requested action")
    

    post_query.delete(synchronize_session=False)

    db.commit()
    return {"message": f"Post {id} has been successfuly deleted"}


@router.put("/{id}", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
async def update_post(new_post: schemas.PostUpdate, id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    # raw sql commands
    # cursor.execute("""UPDATE posts SET title=%s, content=%s WHERE id=%s RETURNING *""", (new_post.title, new_post.content, id))
    # updated_post = cursor.fetchone()
    # conn.commit()

    # sqlalchemy
    post = new_post.model_dump()
    updated_post_query = db.query(models.Post).filter(
        models.Post.id == id)
    
    if not updated_post_query.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Post with id: {id} could not be found ")
    
    if not updated_post_query.first().user_id == current_user.id: # type: ignore
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not authorized to perform requested action")

    updated_post_query.update({models.Post.title: new_post.title,
                              models.Post.content: new_post.content}, synchronize_session=False)
    db.commit()
    return updated_post_query.first()
