# teddy-hospital

## Description

A web application that interfaces with a model that generates fake X-Rays of stuffed animals.

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

## Usage guide

### For Admins

TODO

### For Doctors

As a doctor you can "x-ray" teddybears (and other stuffed animals) with a camera attached to the computer.
Additionally, you can create breaks in the generated x-rays.
All x-rays approved by the doctor can be retrieved by the owner of the patient using a QR code.

#### Before recieving patients

Before recieving patients, you should check somethings to ensure smoth operation of the application.
- make sure you can connect to the website running the application
- check if the computer has a webcam

If you have trouble with reaching the website or getting errors, your admins should be able to help you.

#### Generating QR-codes

Simmilat to real hospitals, each patient needs a unique identifier. In this case we use QR codes.
To generate the QR codes,
- open the admin page
- set a desired amount of QR codes you want
- click generate (this may take some time)
- a PDF containing the QR codes will be downloaded once the generation is done

We recommend printing the QR codes on adhesive paper and sticking it on something that the owner of the patients will not lose easly. (For instance flyers)
**Make sure you do this in advance**
These QR codes are necessary when scanning a patient

#### Scanning a patient

To scan a patient you need:
- the QR code for the patient
- type of animal
- name of owner and patient

The type of animal in this case is used to give the AI model in the background a better idea on what it is looking at.
If type is unclear or non-existent in the list, you can choose "other" in the following step.

To start scanning:
- go to the "Camera" page
- scan the QR code
- input the details of the patient
- take a picture of the patient
- upload the picture of the patient

Once you open the Camera page, start the QR-scanner. It should automaticly pickup a QR code in view of the camera and switch to the next step.
The input page for the patient details needs to be filled in order to take a picture of the patient. After filling in the details you can start the camera with the button on screen.
You will have a live feed of the camera like in the QR scan step. You can take a picture with the button and the taken picture will be shown onscreen.
You can retake a picture with the same button. Only the last taken picture will be uploaded for process.
If you are satisfied with the picture you can upload it with the button on screen.

#### Approving x-ray

Because the application uses AI to create the x-rays, the generated images are not always perfect. Hence we require the doctor to approve the x-ray.
You need to approve the x-rays to view them later.

To approve the generated x-rays:
- go to the "Results" page
- approve or reject the generated images

On the Results page, you can see all generated images from the AI model that are waiting to be approved.
For each image uploaded, the AI model generates multiple x-rays images. Each row contains all the generated images from one uploaded picture.
You can approve an image using the green button, or reject all of them with the red button.
If rejected the AI model trys again and will send the newly generated images again until one is approved.
Once approved the generated image, along with the original images will be uploaded to storage for later retreaval.

#### Viewing recent x-rays (carousel)

To view recently approved x-rays head to the "Carousel" page.
Here you can:
- cycle through recently approved x-rays (automaticly ot manually)
- see a slide show of the recent x-rays in fullscreen

All settings are on the top of the page.
Autoplay: toggle to automaticly cycle through the images
images: set how many images are on screen at the same time
original image: setting to show the original image side by side with the x-ray
fullscreen: enters fullscreen mode, a slide show with only one image at a time. exit with esc.

Additionally you can toggle through the images with the arrow buttons.

## License

TODO
