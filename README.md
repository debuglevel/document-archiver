# Document Archiver

This is a very quick and dirty hack.
Do not expect anything.
The source is aweful.

And it seems that I've somehow hardcoded it to run only with docker. :)

```sh
python3 -m venv venv
source ./venv/bin/activate
pip install -r requirements-dev.txt

uvicorn app.rest.main:fastapi --port=8080 --reload --log-config=app/logging-config.yaml
uvicorn app.rest.main:fastapi --port=8080 --log-config=app/logging-config.yaml

docker compose up --build
```
