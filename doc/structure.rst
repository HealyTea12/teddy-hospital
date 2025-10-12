Structure of the Application
=============================

.. toctree::
   :caption: Structure

Overview
--------

The application is composed of four main systems that interact with each other: **Frontend**, **Backend**, **Storage**, and **GPU Server**.

All AI-related operations are handled by the **GPU Server**, while the remaining components function as parts of a conventional web application.

::

      ┌──────────────────────┐
      │      Frontend        │
      │   (SvelteKit App)    │
      └─────────┬────────────┘
                │
                ▼
      ┌──────────────────────┐
      │       Backend        │
      │   (FastAPI Server)   │
      │ - Routes requests    │
      │ - Manages queue      │
      │ - Handles storage    │
      └────────┬─┬───────────┘
               │ │
               │ │
        ┌──────┘ └───────────┐
        ▼                    ▼
    ┌────────────────┐     ┌────────────────┐
    │   GPU Server   │     │    Storage     │
    │ (AI Processing)│     │ (Seafile API)  │
    └────────────────┘     └────────────────┘



Frontend
--------

The **Frontend** is built using **SvelteKit** and runs on modern browsers such as Chrome.  
It serves as the primary interface for users to interact with the system.

The frontend communicates with the backend by:
- Sending new images to be processed.
- Retrieving images for display (e.g., carousel images).
- Fetching images that require user approval.

Backend
-------

The **Backend**, written in **Python** using **FastAPI**, acts as the central hub of the application.  
It manages all communication between components and routes every operation through itself.

Key responsibilities include:
- Handling user requests and delegating tasks to the GPU Server.
- Managing storage operations, such as creating folders and saving images.
- Using a **job queue** to manage and dispatch user requests efficiently.

For security and simplicity, the backend only accepts **incoming connections** from the frontend and GPU Server.  
Both components **poll** the backend for new data rather than maintaining persistent outgoing connections.

The only **outgoing connection** from the backend is to the **Storage** system, which it accesses via the storage provider’s API (e.g., **Seafile**).

All API routes are described in detail in the **API Documentation** section.

Storage
-------

The application uses **Seafile** for its reference implementation, but any storage solution offering an accessible API can be integrated.

Storage is intentionally separated from the backend to ensure **data persistence** — images remain available even if the backend is offline.

In this design, the backend uploads and retrieves images through the cloud storage’s API, allowing the use of existing, reliable storage services.

GPU Server
----------

This repository does not include the implementation of the GPU Server.

The **GPU Server** handles all AI-related computations and was separated from the backend to allow scalability — multiple high-performance machines can be deployed as needed to handle increased workloads.
