from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class DocumentBase(BaseModel):
    pdf_creation_datetime: datetime
    title: str
    filename: str
    url: str
    data_sha512: str


# used when creating an object
class DocumentCreate(DocumentBase):
    data: bytes


class DocumentGet(DocumentBase):
    id: int
    created_on: datetime

    class Config:
        orm_mode = True
