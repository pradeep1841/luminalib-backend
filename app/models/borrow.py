from sqlalchemy import Boolean, Column, Integer

from app.core.database import Base


class Borrow(Base):
    __tablename__ = "borrow_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    book_id = Column(Integer)
    returned = Column(Boolean, default=False)
