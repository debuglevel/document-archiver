from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, LargeBinary, DateTime
from sqlalchemy.orm import relationship

from .database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    created_on = Column(DateTime, index=False)
    title = Column(String, index=False)
    filename = Column(String, index=False)
    url = Column(String, index=False)
    data = Column(LargeBinary, index=False)
    data_sha512 = Column(String, index=False)
