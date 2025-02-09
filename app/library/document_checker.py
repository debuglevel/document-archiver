import hashlib
import logging
from typing import List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from waybackpy import WaybackMachineCDXServerAPI

from app.library import crud, models, pdf_reader
from app.library import schemas

# URL = "https://www.uni-bamberg.de/pruefungsamt/pruefungstermine/"

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def wayback_run(db: Session, url: str, file_extension: str):
    logger.debug(f"Fetching documents snapshots from Wayback Machine...")

    user_agent = "Mozilla/5.0 (Windows NT 5.1; rv:40.0) Gecko/20100101 Firefox/40.0"
    cdx = WaybackMachineCDXServerAPI(
        url, user_agent, start_timestamp="2000", end_timestamp="2030"
    )
    for item in cdx.snapshots():
        logger.debug(
            f"Fetching documents snapshots from Wayback Machine at {item.datetime_timestamp}..."
        )

        documents = fetch_documents(item.archive_url, file_extension)
        update_documents(db, documents)

        logger.debug(
            f"Fetched documents snapshots from Wayback Machine at {item.datetime_timestamp}"
        )

    logger.debug(f"Fetched documents snapshots from Wayback Machine")


def run(db: Session, url: str, file_extension: str):
    logger.debug(f"Run on {url} with extension {extension}...")
    documents = fetch_documents(url, file_extension)
    update_documents(db, documents)
    logger.debug(f"Ran on {url} with extension {extension}.")


def update_documents(db: Session, documents: List[schemas.DocumentCreate]):
    logger.debug(f"Updating documents...")

    existing_documents = crud.get_documents(
        db
    )  # probably stupid, asking for all. should ask only for given.

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
                pdf_creation_datetime=document.pdf_creation_datetime,
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


def fetch_documents(
        url: str, file_extension: str
) -> List[schemas.DocumentCreate]:
    logger.debug(f"Fetching documents matching '*.{file_extension}' from {url} ...")

    documents: List[schemas.DocumentCreate] = []

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    for link in soup.select(f"a[href$='.{file_extension}']"):
        link_url = urljoin(url, link["href"])
        response = requests.get(link_url)

        if response.status_code == 404:
            logger.debug(f"{link_url} was a 404")
            continue

        # name the pdf files using the last portion of the link
        filename = link["href"].split("/")[-1]
        title = link.text
        data = response.content
        data_sha512 = hashlib.sha512(data).hexdigest()
        pdf_creation_datetime = pdf_reader.get_datetime(data)

        document = schemas.DocumentCreate(
            pdf_creation_datetime=pdf_creation_datetime,
            title=title,
            filename=filename,
            url=link_url,
            data=data,
            data_sha512=data_sha512,
        )

        documents.append(document)

    logger.debug(
        f"Fetched {len(documents)} documents matching '*.{file_extension}' from {url}"
    )
    return documents
