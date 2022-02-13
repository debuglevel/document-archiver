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


def run(db: Session, url: str, file_extension: str):
    documents = fetch_documents(url, file_extension)
    update_documents(db, documents)


def update_documents(db: Session, documents: List[schemas.DocumentCreate]):
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


def fetch_documents(url: str, file_extension: str) -> List[schemas.DocumentCreate]:
    logger.debug(f"Fetching documents matching '*.{file_extension}' from {url} ...")

    documents: List[schemas.DocumentCreate] = []

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    for link in soup.select(f"a[href$='.{file_extension}']"):
        # name the pdf files using the last portion of the link
        filename = link['href'].split('/')[-1]
        title = link.text
        link_url = urljoin(url, link['href'])
        data = requests.get(link_url).content
        data_sha512 = hashlib.sha512(data).hexdigest()
        created_on = datetime.now()

        document = schemas.DocumentCreate(
            created_on=created_on,
            title=title,
            filename=filename,
            url=link_url,
            data=data,
            data_sha512=data_sha512,
        )

        documents.append(document)

    logger.debug(f"Fetched {len(documents)} documents matching '*.{file_extension}' from {url}")
    return documents