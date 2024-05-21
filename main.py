from fastapi import FastAPI
import models
from database import engine
from router import auth, todos, category, product

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(category.router)
app.include_router(product.router)
