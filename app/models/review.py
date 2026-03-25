from sqlalchemy import Column, Integer, String

from app.core.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    book_id = Column(Integer)
    content = Column(String)
