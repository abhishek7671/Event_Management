# Event Management System (FastAPI)

## Overview
This project is an **Event Management System** built with **FastAPI** and **SQLAlchemy**. It allows users to:
- **Create and manage events** (title, description, date, time, capacity)
- **Register attendees** for an event
- **Check-in attendees**
- **List all events and attendees**

## Features
- **JWT Authentication** for user security
- **Event creation, updating, and deletion**
- **Attendee registration with unique email validation**
- **Event capacity handling**
- **Check-in system to mark attendance**

## Installation
### Prerequisites
Ensure you have the following installed:
- Python 3.8+
- PostgreSQL or SQLite
- Virtual environment tool (optional)

### Setup Steps
1. Clone the repository:
   ```sh
   git clone https://github.com/Narsi12/Fatsapi-EventManagementSystem.git
   cd event-management
   ```
2. Create and activate a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   ```sh
   export DATABASE_URL="postgresql://user:password@localhost/dbname"
   export SECRET_KEY="your_secret_key"
   ```
5. Run migrations to set up the database:
   ```sh
   alembic upgrade head
   ```
6. Start the FastAPI server:
   ```sh
   uvicorn main:app --reload
   ```
7. Open API documentation:
   - Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - Redoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## API Endpoints
| Method | Endpoint             | Description                     |
|--------|----------------------|---------------------------------|
| POST   | `/users/login`       | User authentication            |
| POST   | `/events/`           | Create a new event             |
| GET    | `/events/`           | List all events                |
| GET    | `/events/{event_id}` | Get event details              |
| POST   | `/attendees/`        | Register an attendee           |
| GET    | `/attendees/`        | List event attendees           |
| POST   | `/checkin/{attendee_id}` | Mark attendee check-in |

## Project Structure
```
.
├── app/
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas
│   ├── database.py      # Database connection
│   ├── main.py          # FastAPI app setup
│   ├── routes/
│   │   ├── events.py    # Event-related routes
│   │   ├── attendees.py # Attendee routes
│   │   ├── auth.py      # JWT authentication
│   ├── utils.py         # Utility functions
│
├── migrations/          # Alembic migrations
├── .env                 # Environment variables
├── requirements.txt     # Python dependencies
├── README.md            # Project documentation
```

## Contributing
1. Fork the repository
2. Create a new branch: `git checkout -b feature-branch`
3. Make your changes and commit: `git commit -m "Added new feature"`
4. Push to the branch: `git push origin feature-branch`
5. Submit a pull request