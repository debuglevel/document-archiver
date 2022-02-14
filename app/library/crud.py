import logging
from datetime import datetime
from typing import List

from sqlalchemy.orm import Session

from . import models, schemas

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def create_document(db: Session, document: schemas.DocumentCreate):
    db_document = models.Document(
        created_on=datetime.now(),
        pdf_creation_datetime=document.pdf_creation_datetime,
        title=document.title,
        filename=document.filename,
        url=document.url,
        data=document.data,
        data_sha512=document.data_sha512,
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


def get_document(db: Session, user_id: int):
    return db.query(models.Document).filter(models.Document.id == user_id).first()


def get_documents(
    db: Session, skip: int = 0, limit: int = 1000
) -> List[models.Document]:
    logger.debug(f"Getting documents...")
    documents = db.query(models.Document).offset(skip).limit(limit).all()
    logger.debug(f"Got documents")
    return documents
