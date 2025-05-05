# Setup

install python 3.12 and [uv](https://docs.astral.sh/uv/)
install python dependencies via `uv sync`

# Dev

1. Run redis:

```sh
docker run --name redis-server -p 6379:6379 redis
```

2. Run worker:

```sh
uv --directory backend run celery -A src.worker.celery_app worker --loglevel=info
```

3. Run web app

```sh
uv --directory backend run fastapi dev --port 8000 src/app.py
```

4. Test the workflow

```sh
uv --directory backend run python scripts/upload_image.py
uv --directory backend run python scripts/check_result.py
```
