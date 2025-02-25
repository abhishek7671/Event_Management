import pytest
import httpx
from fastapi.testclient import TestClient
from main import app  # Import your FastAPI app from main.py

client = TestClient(app)


@pytest.fixture
def event_data():
    return {"event_id": 1, "name": "Test Event", "max_attendees": 10}


@pytest.fixture
def attendee_data():
    return {
        "first_name": "John",
        "last_name": "Doe",
        "email": "johndoe@example.com",
        "phone_number": "1234567890",
        "event_id": 1
    }


### TEST CASES ###

# 1. Register an attendee successfully
def test_register_attendee(attendee_data):
    response = client.post("/attendees/", json=attendee_data)
    assert response.status_code == 200
    assert response.json()["email"] == attendee_data["email"]


# 2. Register an attendee for a non-existent event
def test_register_attendee_event_not_found(attendee_data):
    attendee_data["event_id"] = 999  # Invalid event ID
    response = client.post("/attendees/", json=attendee_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found"


# 3. Register an attendee when event is fully booked
def test_register_attendee_fully_booked(attendee_data):
    for _ in range(10):  # Max attendees reached
        client.post("/", json=attendee_data)

    response = client.post("/", json=attendee_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Event is fully booked"


# 4. Check in an attendee successfully
def test_check_in_attendee():
    response = client.put("/1/checkin")
    assert response.status_code == 200
    assert response.json()["check_in_status"] is True


# 5. Check in an attendee who does not exist
def test_check_in_non_existent_attendee():
    response = client.put("/999/checkin")
    assert response.status_code == 404
    assert response.json()["detail"] == "Attendee not found"


# 6. Get attendees for an event
def test_get_attendees():
    response = client.get("/attendees", params={"event_id": 1})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# 7. Get attendees for a non-existent event
def test_get_attendees_non_existent_event():
    response = client.get("/attendees", params={"event_id": 999})
    assert response.status_code == 404
    assert response.json()["detail"] == "No attendees found for this event"


# 8. Bulk upload attendees (valid CSV)
def test_bulk_upload_attendees():
    csv_content = "first_name,last_name,email,phone_number,event_id\nJohn,Doe,johndoe@example.com,1234567890,1\nJane,Doe,janedoe@example.com,9876543210,1"
    files = {"file": ("attendees.csv", csv_content)}
    
    response = client.post("/attendee/1/bulk-upload", files=files)
    assert response.status_code == 200
    assert "Successfully added" in response.json()["message"]


# 9. Bulk upload attendees (invalid CSV format)
def test_bulk_upload_invalid_csv():
    csv_content = "wrong_header1,wrong_header2,email\nJohn,Doe,johndoe@example.com"
    files = {"file": ("invalid.csv", csv_content)}
    
    response = client.post("/attendee/1/bulk-upload", files=files)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid CSV format"


# 10. Bulk check-in attendees (valid CSV)
def test_bulk_check_in_attendees():
    csv_content = "email\njohndoe@example.com\njanedoe@example.com"
    files = {"file": ("checkin.csv", csv_content)}

    response = client.post("/attendee/1/bulk-check-in", files=files)
    assert response.status_code == 200
    assert "Successfully checked in" in response.json()["message"]


# 11. Bulk check-in attendees (invalid CSV format)
def test_bulk_check_in_invalid_csv():
    csv_content = "wrong_header\njohndoe@example.com"
    files = {"file": ("invalid_checkin.csv", csv_content)}

    response = client.post("/attendee/1/bulk-check-in", files=files)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid CSV format. Expected headers: 'email'"
