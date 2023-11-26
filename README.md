# Project: Dockerized Flask App with PostgreSQL

## Overview

This project demonstrates a simple Flask web application using Docker for containerization, PostgreSQL for the database, and Python for backend functionality.

## Author

**Lucas Veríssimo Campos dos Santos**
**email: lucas.verissimo@match.mt**

## Project Structure

- **Dockerfile**: Defines the Docker image with Python 3.8, installs project dependencies, exposes port 80, and sets the default command to run the `app.py` script.

- **docker-compose.yml**: Configures the services for the web app and PostgreSQL, specifying dependencies, ports, and environment variables for the database.

- **requirements.txt**: Lists the Python dependencies, including Flask, SQLAlchemy, psycopg2-binary, Werkzeug, and Flask-SQLAlchemy.

- **app.py**: The main Flask application file. It includes database setup, model definitions (ClientList and Client), and API routes for creating clients and retrieving client lists.

## Running the Application

1. Build the Docker image and start the services:

   ```bash
   docker-compose up --build

Access the application at http://localhost:5000.

## API Endpoints

- **POST /client**: Create a new client.

- **GET /client/<list_id>**: Retrieve the list of clients for the specified list ID.

## Database Configuration

- **Database Name**: estudiodigital
- **Username**: adminestudiodigital
- **Password**: passwordestudiodigital

## Notes

- The application waits for the PostgreSQL database to be ready before starting, with a maximum of 30 retries and a retry interval of 2 seconds.

- Each client list can contain up to 100 clients. When the limit is reached or no list exists, a new list is created.

- Client data includes ID, name, email, cellphone, status, and a hashed value.
