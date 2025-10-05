How to for doctors

==================

For Doctors
===========

As a doctor you can "x-ray" teddybears (and other stuffed animals) with a camera attached to the computer.
Additionally, you can create breaks in the generated x-rays.
All x-rays approved by the doctor can be retrieved by the owner of the patient using a QR code.

Before recieving patients
-------------------------
Before recieving patients, you should check somethings to ensure smoth operation of the application.
- make sure you can connect to the website running the application
- check if the computer has a webcam

If you have trouble with reaching the website or getting errors, your admins should be able to help you.

Generating QR-codes
-------------------
Simmilat to real hospitals, each patient needs a unique identifier. In this case we use QR codes.
To generate the QR codes:
- open the admin page
- set a desired amount of QR codes you want
- click generate (this may take some time)
- a PDF containing the QR codes will be downloaded once the generation is done

We recommend printing the QR codes on adhesive paper and sticking it on something that the owner of the patients will not lose easly. (For instance flyers)
**Make sure you do this in advance**
These QR codes are necessary when scanning a patient

Scanning a patient
------------------
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

Approving x-ray
---------------
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

Viewing recent x-rays (carousel)
--------------------------------
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