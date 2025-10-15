Installation Guide
==================

Configure the backend by filling out the ``config.toml.example`` file in the ``backend`` folder and renaming it to ``config.toml``.

Generate a secret key with the following command and copy it into the ``SECRET_KEY`` field:

.. code-block:: bash

   openssl rand -hex 32

Generate a password for using the API with bcrypt using the following Python command, and paste the result into ``PASSWORD_HASH``.  
This password will be used by the frontend and GPU to authenticate.

.. code-block:: bash

   python3 -c "from passlib.context import CryptContext; cc = CryptContext(schemes=['bcrypt'], deprecated='auto'); print(cc.hash('<password>'))"

To set up storage, see the section on the specific storage backend you are using.

Next, configure the frontend by filling out the ``.env.example`` file in the ``frontend`` folder and renaming it to ``.env``.

For production, you must also fill out the ``.env.example`` file in the root directory.  
Here, you can set up your **domain name**, **SSL key**, and **certificate** locations.  
A free SSL certificate can be obtained by following the instructions at:

`Let's Encrypt! <https://letsencrypt.org/>`_

To Start in Development Mode
----------------------------

Install dependencies:

.. code-block:: bash

   pip install -r backend/requirements.txt

Start the backend (by default on port 8000):

.. code-block:: bash

   fastapi dev backend/main.py

Start the frontend (by default on port 5173):

.. code-block:: bash

   cd frontend && npm run dev

Start in Development Mode with Docker
-------------------------------------

Run the following command:

.. code-block:: bash

   docker compose up --build

Start in Production Mode with Docker
------------------------------------

Run the following command:

.. code-block:: bash

   docker compose -f compose-prod.yaml up --build -d
