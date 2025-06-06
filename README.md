# teddy-hospital

## Description

A web application that interfaces with a model that generates fake X-Rays of stuffed animals.

## Instalation Guide

Install dependencies:

```bash
pip install -r backend/requirements.txt
```

Configure the backend by filling up `config.toml.example` in the `backend` folder and renaming it to `config.toml`.
Generate a secret key with `openssl rand -hex 32` and copy into SECRET_KEY.
Generate a password for using the api with bcrypt with `python3 -c "from passlib.context import CryptContext; cc = CryptContext(schemes=['bcrypt'], deprecated='auto'); cc.hash(<password>)"` and past into `PASSWORD_HASH`. This password will be used by the front end and GPU to authenticate.

Configure the frontend by filling up `.env.example` in the `frontend` folder and renaming it to `.env`.

### To start on development mode:

Start the backend (by default on port 8000)

```bash
fastapi dev backend/main.py
```

Start the frontend (by default on port 5173)

```bash
cd frontend && npm run dev
```

### Start on development mode with docker:

Run:

```
docker compose up --build
```

## Usage example

This application can be used at the "Teddybär Krankenhaus" x-ray booth to simulate an appointment at the doctor for a x-ray scan.
No actual x-rays needed.
Doctors can use a webcam to "x-ray" the stuffed animals brought by the visitors.
These "x-rays" can be retrieved by the visitor at a later point with a QR code.

## License

TODO
