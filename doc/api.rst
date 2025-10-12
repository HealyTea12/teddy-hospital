User API
========

.. toctree::
   :caption: API Documentation

Overview
--------

This API provides endpoints for secure QR code generation, image upload/processing, and job/result management.

Authentication is handled via **JWT bearer tokens**, obtained from the ``/token`` endpoint.

All endpoints (except ``/token``) require a valid token in the header::

   Authorization: Bearer <access_token>

Authentication
--------------

**POST** ``/token``

Authenticate using a password and receive a JWT access token.

**Request (Form Data)**

+------------+----------+-----------+----------------------------------+
| Field      | Type     | Required  | Description                      |
+============+==========+===========+==================================+
| password   | string   | ✅        | The application access password. |
+------------+----------+-----------+----------------------------------+

**Response (200 OK)**

.. code-block:: json

   {
       "access_token": "<JWT>",
       "token_type": "bearer"
   }

**Errors**

* ``401 Unauthorized`` – Incorrect password.

QR Code Management
------------------

**GET** ``/qr``

Generates a batch of QR codes in the background.

**Query Parameters**

+-------+----------+-----------+--------------------------------------------+
| Field | Type     | Required  | Description                                |
+=======+==========+===========+============================================+
| n     | integer  | ✅        | Number of QR codes to generate (1–1000).   |
+-------+----------+-----------+--------------------------------------------+

**Response (200 OK)**::

   Generating N QR codes, this may take a while. Check the progress at /qr/progress

**Auth required:** ✅ Yes  
**Background job:** Generates a ``qr.pdf`` file containing all QR codes.

**GET** ``/qr/progress``

Retrieves the current progress of the QR code generation task.

**Response (200 OK)**

.. code-block:: json

   {
       "progress": 72.5
   }

**Auth required:** ✅ Yes

**GET** ``/qr/download``

Downloads the generated PDF file containing QR codes.

**Response (200 OK)**

* File download: ``qr.pdf``  
* ``Content-Type: application/pdf``  
* **Auth required:** ✅ Yes

File Upload
-----------

**POST** ``/upload``

Uploads an animal image and metadata for processing.

**Form Data**

+--------------+-------------+-----------+-------------------------------------------+
| Field        | Type        | Required  | Description                               |
+==============+=============+===========+===========================================+
| file         | UploadFile  | ✅        | The animal image file.                    |
+--------------+-------------+-----------+-------------------------------------------+
| first_name   | string      | ✅        | Owner’s first name.                       |
+--------------+-------------+-----------+-------------------------------------------+
| last_name    | string      | ✅        | Owner’s last name.                        |
+--------------+-------------+-----------+-------------------------------------------+
| animal_name  | string      | ✅        | Name of the animal.                       |
+--------------+-------------+-----------+-------------------------------------------+
| qr_content   | string      | ✅        | QR code value associated with this owner. |
+--------------+-------------+-----------+-------------------------------------------+
| animal_type  | string      | ❌        | Type of animal (default "other").         |
+--------------+-------------+-----------+-------------------------------------------+
| broken_bone  | bool        | ❌        | Whether the animal has a broken bone.     |
+--------------+-------------+-----------+-------------------------------------------+

**Response (200 OK)**

.. code-block:: json

   {
       "status": "success",
       "job_id": 42,
       "current_jobs": 5
   }

**Auth required:** ✅ Yes

Job Management
--------------

**GET** ``/job``

Retrieves the next job in the queue for processing.

**Response**

* ``200 OK`` – Returns an image with job metadata in headers.  
* ``204 No Content`` – No jobs available.

**Response Headers (200 OK)**

+---------------+-------------------------+
| Header        | Description             |
+===============+=========================+
| img_id        | The job ID.             |
+---------------+-------------------------+
| first_name    | Owner’s first name.     |
+---------------+-------------------------+
| last_name     | Owner’s last name.      |
+---------------+-------------------------+
| animal_name   | Name of the animal.     |
+---------------+-------------------------+
| animal_type   | Type of animal.         |
+---------------+-------------------------+

**Auth required:** ✅ Yes

**POST** ``/job``

Submits the processed result for a job.

**Form Data**

+-----------+-------------+-----------+--------------------------------------+
| Field     | Type        | Required  | Description                          |
+===========+=============+===========+======================================+
| image_id  | integer     | ✅        | ID of the job being completed.       |
+-----------+-------------+-----------+--------------------------------------+
| result    | UploadFile  | ✅        | The processed (result) image file.   |
+-----------+-------------+-----------+--------------------------------------+

**Response (200 OK)**

.. code-block:: json

   {
       "status": "success"
   }

**Auth required:** ✅ Yes

**GET** ``/confirm``

Confirms or rejects a job result.

**Query Parameters**

+-----------+------------------+-----------+--------------------------------+
| Field     | Type             | Required  | Description                    |
+===========+==================+===========+================================+
| image_id  | integer          | ✅        | The job ID.                    |
+-----------+------------------+-----------+--------------------------------+
| choice    | integer          | ✅        | Index of chosen result option. |
+-----------+------------------+-----------+--------------------------------+
| confirm   | ConfirmJobEnum   | ✅        | Confirmation status.           |
+-----------+------------------+-----------+--------------------------------+

**Response (200 OK)**

.. code-block:: json

   {
       "status": "success"
   }

**Auth required:** ✅ Yes

Results
-------

**GET** ``/results``

Lists pending job results awaiting confirmation.

**Response (200 OK)**

.. code-block:: json

   {
       "metadata": {
           "1": {"first_name": "Alice", "last_name": "Smith", "animal_name": "Buddy"}
       },
       "results": {
           "1": [
               "http://localhost:8000/results/1/0",
               "http://localhost:8000/results/1/1"
           ]
       },
       "originals": {
           "1": "http://localhost:8000/results/1/original"
       },
       "results_per_image": 2
   }

**Auth required:** ✅ Yes

**GET** ``/results/{job_id}/{option}``

Fetches a specific result or original image.

**Path Parameters**

+----------+----------+-----------------------+
| Field    | Type     | Description           |
+==========+==========+=======================+
| job_id   | integer  | Job identifier.       |
+----------+----------+-----------------------+
| option   | string   | Result index or "original". |
+----------+----------+-----------------------+

**Response (200 OK)**

Returns the image as a stream (``image/png``).

**Cache Control Headers**::

   Cache-Control: no-cache, no-store, must-revalidate
   Pragma: no-cache
   Expires: 0

Animal Types
------------

**GET** ``/animal_types``

Retrieves the available animal types supported by the system.

**Response (200 OK)**

.. code-block:: json

   {
       "types": ["dog", "cat", "horse", "other"]
   }

Carousel
--------

**GET** ``/carousel``

Lists URLs to carousel images.

**Response (200 OK)**

.. code-block:: json

   [
       "http://localhost:8000/carousel/0",
       "http://localhost:8000/carousel/1"
   ]

**GET** ``/carousel/{index}``

Downloads a ZIP file containing both X-ray and original images for a carousel item.

**Path Parameters**

+---------+----------+-------------------------+
| Field   | Type     | Description             |
+=========+==========+=========================+
| index   | integer  | Carousel image index.   |
+---------+----------+-------------------------+

**Response (200 OK)**

* File: ``carousel_<index>.zip``  
* MIME: ``application/zip``  
* Contents: ``xray.png``, ``original.png``

**Errors**

* ``404 Not Found`` – Invalid index.

Global Variables
----------------

+------------------------+-------------------------------------------+
| Variable               | Description                               |
+========================+===========================================+
| qr_generation_progress | Tracks progress of QR code generation.    |
+------------------------+-------------------------------------------+

Notes
-----

* All endpoints except ``/token``, ``/animal_types``, and ``/carousel`` require JWT authentication.  
* The system uses **bcrypt** for password hashing and **JWT** for token encoding.  
* QR code PDFs are generated with **ReportLab**.  
* Uploaded images and results are managed via a custom **JobQueue** system.


.. automodule:: teddy_hospital
    :members:
