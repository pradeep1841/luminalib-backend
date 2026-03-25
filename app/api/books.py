import os

from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import SessionLocal
from app.models.book import Book
from app.models.borrow import Borrow
from app.models.review import Review
from app.models.user import User
from app.services.ai import generate_summary

router = APIRouter()


# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 📚 Upload Book + Async Summary
@router.post("/books")
def upload_book(
    title: str,
    author: str,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    os.makedirs("storage", exist_ok=True)

    file_location = f"storage/{file.filename}"

    with open(file_location, "wb") as f:
        content = file.file.read()
        f.write(content)

    new_book = Book(title=title, author=author, file_path=file_location)

    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    # 🔥 Background summary task
    def process_summary(book_id, content):
        summary = generate_summary(content.decode(errors="ignore"))

        db2 = SessionLocal()
        book = db2.query(Book).filter(Book.id == book_id).first()
        if book:
            book.summary = summary
            db2.commit()
        db2.close()

    if background_tasks:
        background_tasks.add_task(process_summary, new_book.id, content)

    return {"message": "Book uploaded, summary processing..."}


# 📥 Borrow Book
@router.post("/books/{book_id}/borrow")
def borrow_book(
    book_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    db_user = db.query(User).filter(User.email == user["sub"]).first()

    borrow = Borrow(user_id=db_user.id, book_id=book_id)

    db.add(borrow)
    db.commit()

    return {"message": "Book borrowed"}


# 🔄 Return Book
@router.post("/books/{book_id}/return")
def return_book(
    book_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    db_user = db.query(User).filter(User.email == user["sub"]).first()

    borrow = (
        db.query(Borrow)
        .filter(
            Borrow.book_id == book_id,
            Borrow.user_id == db_user.id,
            Borrow.returned.is_(False)
        )
        .first()
    )

    if not borrow:
        return {"error": "No active borrow found"}

    borrow.returned = True
    db.commit()

    return {"message": "Book returned"}


# ⭐ Add Review (only if borrowed)


@router.post("/books/{book_id}/reviews")
def add_review(
    book_id: int,
    content: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    db_user = db.query(User).filter(User.email == user["sub"]).first()

    # check borrow
    borrow = (
        db.query(Borrow)
        .filter(
            Borrow.book_id == book_id,
            Borrow.user_id == db_user.id,
            Borrow.returned.is_(False)
        )
        .first()
    )

    if not borrow:
        return {"error": "You must borrow the book before reviewing"}

    # 🔥 sentiment logic (yahi add karna hai)
    positive_words = ["good", "great", "amazing", "awesome"]

    sentiment = "neutral"
    for word in positive_words:
        if word in content.lower():
            sentiment = "positive"

    review = Review(user_id=db_user.id, book_id=book_id, content=content)

    db.add(review)
    db.commit()

    return {"message": "Review added", "sentiment": sentiment}  # optional but good 🔥


# 🤖 Get Book Analysis (Summary)
@router.get("/books/{book_id}/analysis")
def get_analysis(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()

    if not book:
        return {"error": "Book not found"}

    return {"title": book.title, "summary": book.summary}


@router.get("/recommendations")
def get_recommendations(db: Session = Depends(get_db), user=Depends(get_current_user)):
    db_user = db.query(User).filter(User.email == user["sub"]).first()

    # user ke borrowed books
    borrows = db.query(Borrow).filter(Borrow.user_id == db_user.id).all()

    book_ids = [b.book_id for b in borrows]

    # un books ke authors
    books = db.query(Book).filter(Book.id.in_(book_ids)).all()

    authors = [b.author for b in books]

    # same author ke aur books recommend karo
    recommendations = db.query(Book).filter(Book.author.in_(authors)).all()

    return {
        "recommendations": [
            {"id": b.id, "title": b.title, "author": b.author} for b in recommendations
        ]
    }


@router.get("/books")
def list_books(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    books = db.query(Book).offset(skip).limit(limit).all()

    return [{"id": b.id, "title": b.title, "author": b.author} for b in books]


@router.delete("/books/{book_id}")
def delete_book(
    book_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    book = db.query(Book).filter(Book.id == book_id).first()

    if not book:
        return {"error": "Book not found"}

    # file delete karo

    if os.path.exists(book.file_path):
        os.remove(book.file_path)

    # DB se delete
    db.delete(book)
    db.commit()

    return {"message": "Book deleted successfully"}
