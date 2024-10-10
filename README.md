# Assignment Submission Portal

## Overview
This project implements a backend system for an assignment submission portal using FastAPI and MongoDB. It enables users to submit assignments and administrators to review and manage these submissions efficiently.

## Features
- User and Admin authentication
- Assignment submission for users
- Assignment review (accept/reject) functionality for admins
- MongoDB integration for scalable data storage
- Basic authentication for secure access

## Technology Stack
- FastAPI: A modern, fast (high-performance) web framework for building APIs with Python
- MongoDB: A source-available cross-platform document-oriented database
- Python 3.7+: The programming language used
- Pydantic: Data validation and settings management using Python type annotations

## Setup and Installation

1. Clone the repository:
2. Install dependencies: pip install -r requirements.txt
3. Ensure MongoDB is running on your system.
4. Start the FastAPI server: python main.py

The API will be available at `http://127.0.0.1:8009`.

## API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/register` | Register a new user or admin | No |
| POST | `/upload` | Upload a new assignment | Yes (User) |
| GET | `/assignments` | Retrieve all assignments | Yes (Admin) |
| POST | `/assignments/{assignment_id}/accept` | Accept an assignment | Yes (Admin) |
| POST | `/assignments/{assignment_id}/reject` | Reject an assignment | Yes (Admin) |
| GET | `/admins` | Retrieve all admin users | Yes |

## Authentication
This project uses Basic Authentication. Include the appropriate credentials in the Authorization header of your requests.

## Testing
Use tools like Postman or curl to test the API endpoints. Ensure you include the appropriate headers and authentication for each request.
