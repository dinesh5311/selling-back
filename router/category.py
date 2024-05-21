from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from pydantic import BaseModel, Field
from database import SessionLocal
from sqlalchemy.orm import Session
from .auth import get_current_user
from models import Category

router = APIRouter(
    prefix='/category',
    tags=["category"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class CategoryRequest(BaseModel):
    name: str = Field()
    description: str = Field()


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all_catogories(db: db_dependency):
    return db.query(Category).all()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_category(db: db_dependency, category: CategoryRequest):
    try:
        existing_category = db.query(Category).filter(Category.name == category.name).first()
        if existing_category:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category already exists")

        category_model = Category(**category.dict())
        db.add(category_model)
        db.commit()
        db.refresh(category_model)
        return category_model
    except Exception as e:
        db.rollback()
        print(f"An error occurred: {str(e)}")
        if e.status_code == status.HTTP_409_CONFLICT:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category already exists")
        raise HTTPException(status_code=500, detail="An error occurred while creating a new category")
