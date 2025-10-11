# teddy-hospital

## Description


The Teddy Bear Hospital project transforms images of stuffed animals into "pseudo-x-ray images" using AI diffusion technology. This offers an interactive and modern alternative to traditional, pre-printed skeleton drawings and allows for higher accuracy and personalization. The resulting images can be viewed directly on-site and accessed online, allowing children to take their "x-rayed" stuffed animal home as a unique souvenir.

This project was completed by a group of six Computer Science Bsc. Students at Heidelberg University during summer semester 2025. As such, this project will most likely not be maintained.

### Before

![Caputred image](samples/bluemonkey_pre.png)

### After

![Generated x-ray](samples/bluemonkey_post.png)

## Instalation Guide

Configure the backend by filling up `config.toml.example` in the `backend` folder and renaming it to `config.toml`.
Generate a secret key with `openssl rand -hex 32` and copy into SECRET_KEY.
Generate a password for using the api with bcrypt with `python3 -c "from passlib.context import CryptContext; cc = CryptContext(schemes=['bcrypt'], deprecated='auto'); cc.hash(<password>)"` and past into `PASSWORD_HASH`. This password will be used by the front end and GPU to authenticate.
To setup storage, see the section on the specific storage you are using.

Configure the frontend by filling up `.env.example` in the `frontend` folder and renaming it to `.env`.

For production you must also fill out the `.env.example` file on the root directory. There you can setup your domain name and the location of your SSL key and certificate. A certificate can be obtained, for example, by following the instructions at [Let's Encrypt!](https://letsencrypt.org/).

### To start on development mode:

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

### Start on development mode with docker:

Run:

```
docker compose up --build
```

### Start on production mode using docker

Run the following command:

```
docker compose -f compose-prod.yaml up --build -d
```

## Configure Storage

### Seafile

The best way of configuring seafile is with the repo token. That makes sure that in case the repo token is leaked,
that nobody has access to the rest of your seafile account. To generate such a token you can either follow the GUI
via "Library context menu (the three dots next to the library name) -> Advanced -> API Token". However, teddy-hospital only works with a repo token if the seafile API is of version >= 12.

In case your Seafile is version < 12, you should use your account token. You can get it by running:

```
curl --request POST \
     --url <seafile_url>/api2/auth-token/ \
     [--header 'X-SEAFILE-OTP: <otp>'] \
     --header 'accept: application/json' \
     --header 'content-type: application/json' \
     --data '
{
  "username": <username>,
  "password": <password>
}
'
```

The 'X-SEAFILE-OTP' is the 6 digit code you get usually on your phone in case two factor authentification is activated. You can also get the account token through the GUI.

If you are really lazy and don't want to generate the tokens, you can also just put in your username and password. Only one of these authentication methods needs to be present and you can delete the ones you are not using from the `config.toml`.

## Usage example

This application can be used at the "Teddybär Krankenhaus" x-ray booth to simulate an appointment at the doctor for a x-ray scan.
No actual x-rays needed.
Doctors can use a webcam to "x-ray" the stuffed animals brought by the visitors.
These "x-rays" can be retrieved by the visitor at a later point with a QR code.


## License

TODO
