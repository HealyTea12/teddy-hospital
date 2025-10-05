Instalation Guide
=================


Configure the backend by filling up `config.toml.example` in the `backend` folder and renaming it to `config.toml`.
Generate a secret key with `openssl rand -hex 32` and copy into SECRET_KEY.
Generate a password for using the api with bcrypt with `python3 -c "from passlib.context import CryptContext; cc = CryptContext(schemes=['bcrypt'], deprecated='auto'); cc.hash(<password>)"` and past into `PASSWORD_HASH`. This password will be used by the front end and GPU to authenticate.
To setup storage, see the section on the specific storage you are using.

Configure the frontend by filling up `.env.example` in the `frontend` folder and renaming it to `.env`.

For production you must also fill out the `.env.example` file on the root directory. There you can setup your domain name and the location of your SSL key and certificate. A certificate can be obtained, for example, by following the instructions at [Let's Encrypt!](https://letsencrypt.org/).

To start on development mode:
-----------------------------
Install dependencies:

```bash
pip install -r backend/requirements.txt
```

Start the backend (by default on port 8000)

```bash
fastapi dev backend/main.py
```

Start the frontend (by default on port 5173)

```bash
cd frontend && npm run dev
```

Start on development mode with docker:
--------------------------------------
Run:

```
docker compose up --build
```

Start on production mode using docker
-------------------------------------
Run the following command:

```
docker compose -f compose-prod.yaml up --build -d