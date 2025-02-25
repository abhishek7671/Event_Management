import pytest
from fastapi.testclient import TestClient
from main import app
from datetime import datetime
from database import SessionLocal
from models import Event, EventStatus
from schemas import EventCreate, EventUpdate
from sqlalchemy.orm import declarative_base
Base = declarative_base() 

client = TestClient(app)

@pytest.fixture
def db():
    """Fixture to provide a test database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_create_event(db):
    """Test creating a new event."""
    event_data = {
        "name": "Tech Conference",
        "description": "A conference on AI and cloud computing",
        "location": "New York",
        "status": "scheduled",
        "date": "2025-03-15T10:00:00",
        "start_time": "2025-03-15T10:00:00",   
        "end_time": "2025-03-15T17:00:00", 
        "max_attendees": 200
    }

    response = client.post("/events/", json=event_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == event_data["name"]
    assert data["location"] == event_data["location"]



def test_update_event(db):
    """Test updating an existing event."""
    event = Event(
    name="Tech Meetup",
    description="Networking event",
    location="San Francisco",
    status=EventStatus.scheduled,
    date=datetime.fromisoformat("2025-05-10T15:00:00"),  # Use the correct field name
    max_attendees=100
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    update_data = {"description": "Updated Networking event"}
    response = client.put(f"/events/{event.event_id}", json=update_data)
    print(response.json())

    assert response.status_code == 200
    data = response.json()
    assert data["description"] == update_data["description"]

def test_list_events(db):
    """Test listing events with optional filters."""
    response = client.get("/events/")
    assert response.status_code in [200, 404]

    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)
