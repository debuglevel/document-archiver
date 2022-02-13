from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


# class ItemBase(BaseModel):
#     title: str
#     description: Optional[str] = None
#
#
# class ItemCreate(ItemBase):
#     pass
#
#
# class Item(ItemBase):
#     id: int
#     owner_id: int
#
#     class Config:
#         orm_mode = True
#
#
# class UserBase(BaseModel):
#     email: str
#
#
# class UserCreate(UserBase):
#     password: str
#
#
# class User(UserBase):
#     id: int
#     is_active: bool
#     items: List[Item] = []
#
#     class Config:
#         orm_mode = True


class DocumentBase(BaseModel):
    created_on: datetime
    title: str
    filename: str
    url: str
    data: bytes
    data_sha512: str


# used when creating an object
class DocumentCreate(DocumentBase):
    pass


# used when returning an object (additional attributes are known)
class Document(DocumentBase):
    id: int

    class Config:
        orm_mode = True
