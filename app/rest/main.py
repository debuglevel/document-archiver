#!/bin/usr/python3
import logging.config
from typing import Optional
from fastapi import FastAPI

import app.library.person
from app.library import health
from app.library.document_checker import get_all_documents, update_documents
from app.rest.person import PersonIn, PersonOut

from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from fastapi_restful.session import FastAPISessionMaker
from fastapi_restful.tasks import repeat_every

from app.library import crud, models, schemas
from app.library.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

fastapi = FastAPI()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@fastapi.get("/health")
def get_health():
    logger.debug("Received GET request on /health")
    return health.get_health()


@fastapi.get("/health_async")
async def get_health_async():
    logger.debug("Received GET request on /health_async")
    return await health.get_health_async()


@fastapi.get("/")
def read_root():
    return {"Hello": "World"}


# @fastapi.get("/greetings/{greeting_id}")
# async def read_item(greeting_id: int, language: Optional[str] = None):
#     return {"greeting_id": greeting_id, "language": language, "greeting": f"Say Hello to ID {greeting_id} in {language}"}
#
# @fastapi.post("/persons/", response_model=PersonOut)
# async def post_person(input_person: PersonIn):
#     person: app.library.person.Person = await app.library.person.create_person(input_person.name)
#     return PersonOut(name=person.name, created_on=person.created_on)
#
# @fastapi.get("/persons/{name}", response_model=PersonOut)
# async def get_person(name: str):
#     person: app.library.person.Person = await app.library.person.get_person(name)
#     return PersonOut(name=person.name, created_on=person.created_on)


@fastapi.get("/documents/", response_model=List[schemas.Document])
def read_documents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    documents = crud.get_documents(db, skip=skip, limit=limit)
    return documents


@fastapi.get("/documents_/", response_model=List[schemas.Document])
def read_documentsX(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    documents = get_all_documents("https://www.uni-bamberg.de/pruefungsamt/pruefungstermine/", "pdf")
    update_documents(db, documents)


@fastapi.get("/documents/{documents_id}", response_model=schemas.Document)
def read_documents(documents_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_document(db, user_id=documents_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return db_user


@fastapi.on_event("startup")
@repeat_every(seconds=60)
def check_for_new_documents() -> None:
    logger.info("periodic thing...")


# def main():
#     logger.info("Starting...")
#
#     # sleeptime = int(os.environ['SLEEP_INTERVAL'])
#
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--some-host", help="some host", type=str, default="localhost")
#     parser.add_argument("--some-port", help="some port", type=int, default=8080)
#     args = parser.parse_args()
#     # args.some_port
#     # args.some_host
#
#     uvicorn.run(fastapi, host="0.0.0.0", port=8080)
#
#
#


def main():
    import uvicorn
    import yaml
    logging.config.dictConfig(yaml.load(open("app/logging-config.yaml", 'r')))  # configured via cmdline
    logger.info("Starting via main()...")
    uvicorn.run(fastapi, host="0.0.0.0", port=8080)


# This only runs if the script is called instead of uvicorn; should probably not be used.
if __name__ == "__main__":
    main()






# from typing import List
#
# from fastapi import Depends, FastAPI, HTTPException
# from sqlalchemy.orm import Session
#
# from . import crud, models, schemas
# from .database import SessionLocal, engine
#
# models.Base.metadata.create_all(bind=engine)
#
# app = FastAPI()





# @app.post("/users/", response_model=schemas.User)
# def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     db_user = crud.get_user_by_email(db, email=user.email)
#     if db_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
#     return crud.create_user(db=db, user=user)




#
# @app.post("/users/{user_id}/items/", response_model=schemas.Item)
# def create_item_for_user(
#     user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
# ):
#     return crud.create_user_item(db=db, item=item, user_id=user_id)
#
#
# @app.get("/items/", response_model=List[schemas.Item])
# def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     items = crud.get_items(db, skip=skip, limit=limit)
#     return items