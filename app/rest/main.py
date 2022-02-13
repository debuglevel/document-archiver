#!/bin/usr/python3
import logging.config
import pprint
from typing import Optional
from fastapi import FastAPI


from app.library import health, document_checker


from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from fastapi_restful.session import FastAPISessionMaker
from fastapi_restful.tasks import repeat_every


from app.library import crud, models, schemas
from app.library.database import SessionLocal, engine
from fastapi.staticfiles import StaticFiles

models.Base.metadata.create_all(bind=engine)

fastapi = FastAPI()
fastapi.mount("/static", StaticFiles(directory="static", html = True), name="static")


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


@fastapi.get("/documents/", response_model=List[schemas.DocumentGet])
def read_documents(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    documents = crud.get_documents(db, skip=skip, limit=limit)
    return documents


@fastapi.get("/documents/{documents_id}", response_model=schemas.DocumentGet)
def read_documents(documents_id: int, db: Session = Depends(get_db)):
    db_document = crud.get_document(db, user_id=documents_id)
    if db_document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return db_document


@fastapi.get("/documents_manual_trigger/", response_model=List[schemas.DocumentGet])
def check_documents_manually(db: Session = Depends(get_db)):
    document_checker.run(db, "https://www.uni-bamberg.de/pruefungsamt/pruefungstermine/", "pdf")


@fastapi.on_event("startup")
@repeat_every(seconds=60)
def check_documents() -> None:
    logger.debug("Periodically checking for changed documents...")

    # TODO: Depends(db) does not work here.
    # document_checker.run(db, "https://www.uni-bamberg.de/pruefungsamt/pruefungstermine/", "pdf")

    # TODO: Calling my own HTTP API instead.
    from fastapi.testclient import TestClient
    client = TestClient(fastapi)
    client.get("/documents_manual_trigger")


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