# teddy-hospital

## Description

A web application that interfaces with a model that generates fake X-Rays of stuffed animals.

## Instalation Guide

Install dependencies:

```bash
pip install -r backend/requirements.txt
```

### To start on development mode:

Start the backend (by default on port 8000)

```bash
fastapi dev backend/main.py
```

Start the frontend (by default on port 5173)

```bash
cd frontend && npm run dev
```

## Usage example

This application can be used at the "Teddybär Krankenhaus" x-ray booth to simulate an appointment at the doctor for a x-ray scan.
No actual x-rays needed.
Doctors can use a webcam to "x-ray" the stuffed animals brought by the visitors.
These "x-rays" can be retrieved by the visitor at a later point with a QR code.

## License

TODO
