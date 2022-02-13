import os
from typing import List
import logging

import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import hashlib
from datetime import datetime

from sqlalchemy.orm import Session

from app.library import crud, models
from app.library import schemas

# URL = "https://www.uni-bamberg.de/pruefungsamt/pruefungstermine/"

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def update_documents(db: Session, documents: List[schemas.Document]):
    logger.debug(f"Updating documents...")

    existing_documents = crud.get_documents(db)  # probably stupid, asking for all. should ask only for given.

    for document in documents:
        logger.debug(f"Searching for document with SHA512 {document.data_sha512}")
        already_existing = False
        for existing_document in existing_documents:
            if existing_document.data_sha512 == document.data_sha512:
                logger.debug(f"Found document with SHA512 {document.data_sha512}")
                already_existing = True
        if not already_existing:
            logger.debug(f"Document not existing; adding...")
            crud_document = models.Document(
                created_on=document.created_on,
                title=document.title,
                filename=document.filename,
                url=document.url,
                data=document.data,
                data_sha512=document.data_sha512,
            )
            crud.create_document(db, crud_document)
        else:
            logger.debug(f"Document already existing")

    logger.debug(f"Updated documents")


def get_all_documents(root_url: str, file_extension: str) -> List[schemas.Document]:
    logger.debug(f"Getting documents matching '*.{file_extension}' from {root_url} ...")

    documents: List[schemas.Document] = []

    response = requests.get(root_url)
    soup = BeautifulSoup(response.text, "html.parser")

    for link in soup.select(f"a[href$='.{file_extension}']"):
        # name the pdf files using the last portion of the link
        filename = link['href'].split('/')[-1]
        title = link.text
        url = urljoin(root_url, link['href'])
        data = requests.get(url).content
        data_sha512 = hashlib.sha512(data).hexdigest()
        created_on = datetime.now()

        document = schemas.Document(
            id=-1,
            created_on=created_on,
            title=title,
            filename=filename,
            url=url,
            data=data,
            data_sha512=data_sha512,
        )

        documents.append(document)

    logger.debug(f"Got {len(documents)} documents matching '*.{file_extension}' from {root_url}")
    return documents
