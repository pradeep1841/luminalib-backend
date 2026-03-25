from fastapi import FastAPI

from app.api import auth, books
from app.core.database import Base, engine

# ✅ pehle app banao
app = FastAPI()

# ✅ DB tables create karo
Base.metadata.create_all(bind=engine)

# ✅ routers add karo
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(books.router, tags=["Books"])


# test route
@app.get("/")
def home():
    return {"message": "LuminaLib started 🚀"}
