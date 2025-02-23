import logging
from datetime import datetime
from typing import List

from sqlalchemy.orm import Session

from . import models, schemas

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def create_document(database: Session, document: schemas.DocumentCreate):
    logger.debug(f"Creating document {document}...")
    database_document = models.Document(
        created_on=datetime.now(),
        pdf_creation_datetime=document.pdf_creation_datetime,
        title=document.title,
        filename=document.filename,
        url=document.url,
        data=document.data,
        data_sha512=document.data_sha512,
    )

    logger.debug(f"Adding document to database...")
    database.add(database_document)

    logger.debug(f"Committing transaction...")
    database.commit()

    logger.debug(f"Refreshing database...")
    database.refresh(database_document)

    logger.debug(f"Created document {database_document}.")
    return database_document


def get_document(database: Session, document_id: int):
    logger.debug(f"Getting document with ID {document_id}...")

    document = (database
                .query(models.Document)
                .filter(models.Document.id == document_id)
                .first())

    logger.debug(f"Got document with ID {document_id}.")
    return document


def get_documents(database: Session, skip: int = 0, limit: int = 1000) -> List[models.Document]:
    logger.debug(f"Getting documents...")

    documents = (database
                 .query(models.Document)
                 .offset(skip)
                 .limit(limit)
                 .all())

    logger.debug(f"Got documents")
    return documents
