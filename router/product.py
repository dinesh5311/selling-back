from fastapi import APIRouter, Depends, HTTPException, status, Path
from typing import Annotated
from pydantic import BaseModel, Field
from database import SessionLocal
from sqlalchemy.orm import Session
from .auth import get_current_user
from models import Category, Product
from sqlalchemy import func


router = APIRouter(
    prefix='/product',
    tags=["product"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class ProductRequest(BaseModel):
    name: str = Field()
    description: str = Field()
    price: float = Field()
    stock_quantity: int = Field()
    category_id: int = Field(gt=0)


# GET get all products
@router.get("/", status_code=status.HTTP_200_OK)
async def read_all_products(db: db_dependency):
    return db.query(Product).all()


# POST create a product
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_product(db: db_dependency, product: ProductRequest):
    try:
        product_model = Product(**product.dict())
        db.add(product_model)
        db.commit()
        db.refresh(product_model)
        return "Product Added !"
    except Exception as e:
        db.rollback()
        print(f"An error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while adding new product")


# GET product by Category id
@router.get("/category/{category_id}")
async def get_product_by_id(db: db_dependency, category_id: int = Path(gt=0)):
    product_model = db.query(Product).filter(Product.category_id == category_id).first()
    if product_model:
        return product_model
    raise HTTPException(status_code=404, detail="Product not found")

# GET product by product name
@router.get("/name/{product_name}" , status_code=status.HTTP_200_OK)
async def get_product_by_name(db: db_dependency, product_name: str):
    product_model = db.query(Product).filter(func.lower(func.trim(Product.name)) == product_name.strip().lower()).first()
    if product_model:
        return product_model
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

