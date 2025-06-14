#!/bin/usr/python3
import logging.config
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi import Response
from fastapi.staticfiles import StaticFiles
from fastapi_restful.tasks import repeat_every
from sqlalchemy.orm import Session

from app.library import crud, models, schemas
from app.library import health, document_checker
from app.library.database import SessionLocal, engine
import uvicorn
import yaml

SCRAPE_URL = "https://www.uni-bamberg.de/pruefungsamt/pruefungstermine/"

models.Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

fastapi = FastAPI()
fastapi.mount("/static", StaticFiles(directory="static", html=True), name="static")


# Dependency
def get_database():
    logger.debug("Getting database...")
    database = SessionLocal()
    try:
        yield database
    finally:
        logger.debug("Closing database...")
        database.close()


@fastapi.get("/health")
def get_health():
    logger.debug("Received GET request on /health...")
    return health.get_health()


@fastapi.get("/health_async")
async def get_health_async():
    logger.debug("Received GET request on /health_async...")
    return await health.get_health_async()


@fastapi.get("/documents/", response_model=List[schemas.DocumentGet])
def get_documents(skip: int = 0, limit: int = 1000, database: Session = Depends(get_database)):
    logger.debug("Received GET request on /documents...")
    documents = crud.get_documents(database, skip=skip, limit=limit)
    return documents


@fastapi.get("/documents/{document_id}", response_model=schemas.DocumentGet)
def get_document(document_id: int, database: Session = Depends(get_database)):
    logger.debug(f"Received GET request on /documents/{document_id}...")

    database_document = crud.get_document(database, document_id=document_id)

    if database_document is None:
        logger.warning(f"Document with ID {document_id} not found.")
        raise HTTPException(status_code=404, detail="Document not found")

    return database_document


@fastapi.get("/documents_download/{document_id}")
def download_document(document_id: int, database: Session = Depends(get_database)):
    logger.debug(f"Received GET request on /documents_download/{document_id}...")

    database_document: models.Document = crud.get_document(database, document_id=document_id)

    if database_document is None:
        logger.warning(f"Document with ID {document_id} not found.")
        raise HTTPException(status_code=404, detail="Document not found")

    return Response(content=database_document.data, media_type="application/pdf")


@fastapi.get("/documents_manual_trigger/", response_model=List[schemas.DocumentGet])
def check_documents_manually(database: Session = Depends(get_database)):
    logger.debug(f"Received GET request on /documents_manual_trigger/")

    document_checker.run(database, SCRAPE_URL, "pdf")


@fastapi.get("/documents_manual_trigger_wayback/", response_model=List[schemas.DocumentGet])
def check_documents_manually_wayback(database: Session = Depends(get_database)):
    logger.debug(f"Received GET request on /documents_manual_trigger_wayback/")

    document_checker.wayback_run(database, SCRAPE_URL, "pdf")


@fastapi.on_event("startup")
@repeat_every(seconds=60 * 60)
def check_documents() -> None:
    logger.debug("Periodically checking for changed documents...")

    # TODO: Calling my own HTTP API instead.
    from fastapi.testclient import TestClient
    client = TestClient(fastapi)
    client.get("/documents_manual_trigger/")


def main():
    logging.config.dictConfig(
        yaml.safe_load(open("app/logging-config.yaml", "r"))
    )  # configured via cmdline

    logger.info("Starting via main()...")

    uvicorn.run(fastapi, host="0.0.0.0", port=8080)


# This only runs if the script is called instead of uvicorn; should probably not be used.
if __name__ == "__main__":
    main()
