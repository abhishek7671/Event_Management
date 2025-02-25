from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import pandas as pd
import io
import csv
from io import StringIO
from typing import List

from database import get_db, SessionLocal
from models import Attendee, Event
from schemas import AttendeeCreate, AttendeeResponse
from auth import token_required


router = APIRouter()

@router.post("/", response_model=AttendeeResponse)
def register_attendee(attendee: AttendeeCreate, db: Session = Depends(get_db), user: dict = Depends(token_required)):
    try:
        # Check if the event exists
        event = db.query(Event).filter(Event.event_id == attendee.event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        # Check if the event is fully booked
        attendee_count = db.query(Attendee).filter(Attendee.event_id == attendee.event_id).count()
        if attendee_count >= event.max_attendees:
            raise HTTPException(status_code=400, detail="Event is fully booked")

        # Register the new attendee
        new_attendee = Attendee(**attendee.dict())
        db.add(new_attendee)
        db.commit()
        db.refresh(new_attendee)

        return new_attendee
    except ValueError as ve:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Invalid data: {str(ve)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")



@router.put("/{attendee_id}/checkin", response_model=AttendeeResponse)
def check_in_attendee(attendee_id: int, db: Session = Depends(get_db), user: dict = Depends(token_required)):
    try:
        # Check if the attendee exists
        attendee = db.query(Attendee).filter(Attendee.attendee_id == attendee_id).first()
        if not attendee:
            raise HTTPException(status_code=404, detail="Attendee not found")

        # Update check-in status
        attendee.check_in_status = True
        db.commit()
        db.refresh(attendee)

        return attendee
    except ValueError as ve:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Invalid data: {str(ve)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")



@router.get("/attendees", response_model=List[dict])
async def get_attendees(event_id: int, db: Session = Depends(get_db), user: dict = Depends(token_required)):
    """
    Fetch all attendees based on event_id.
    """
    try:
        # Query attendees for the given event ID
        attendees = db.query(Attendee).filter(Attendee.event_id == event_id).all()

        if not attendees:
            raise HTTPException(status_code=404, detail="No attendees found for this event")

        # Convert attendees to a list of dictionaries
        attendees_list = [
            {
                "attendee_id": a.attendee_id,
                "first_name": a.first_name,
                "last_name": a.last_name,
                "email": a.email,
                "phone": a.phone_number,
                "event_id": a.event_id,
                "check_in_status": a.check_in_status  # Assuming this field exists
            }
            for a in attendees
        ]

        return attendees_list  # Return the final list

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(ve)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")




@router.post("/attendee/{event_id}/bulk-upload")
def bulk_upload_attendees(event_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), user: dict = Depends(token_required)):
    """
    Bulk upload attendees for a given event from a CSV file.
    """
    try:
        # Check if the event exists
        event = db.query(Event).filter(Event.event_id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        # Check max attendees constraint
        existing_attendees = db.query(Attendee).filter(Attendee.event_id == event_id).count()
        if existing_attendees >= event.max_attendees:
            raise HTTPException(status_code=400, detail="Max attendees limit reached")
        
        # Read and parse CSV file
        contents = file.file.read().decode("utf-8")
        file.file.seek(0)
        csv_reader = csv.reader(StringIO(contents))
        
        headers = next(csv_reader, None)  # Read the header row
        expected_headers = ["first_name", "last_name", "email", "phone_number", "event_id"]
        
        if not headers or headers != expected_headers:
            raise HTTPException(status_code=400, detail="Invalid CSV format")
        
        attendees_to_add = []
        added_emails = set()  # Track added emails to avoid duplicates

        for row in csv_reader:
            try:
                # Unpack row values
                first_name, last_name, email, phone_number, event_id_csv = row

                # Ensure event_id in CSV matches the provided event_id
                if int(event_id_csv) != event_id:
                    continue  # Skip mismatched event_id
                
                # Skip duplicate attendees (already in DB or within current batch)
                if db.query(Attendee).filter(Attendee.email == email, Attendee.event_id == event_id).first() or email in added_emails:
                    continue
                
                # Stop adding attendees if the max limit is reached
                if existing_attendees + len(attendees_to_add) >= event.max_attendees:
                    break

                # Add valid attendee to the list
                attendees_to_add.append(Attendee(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone_number=phone_number,
                    event_id=event_id
                ))
                added_emails.add(email)

            except ValueError:
                continue  # Skip invalid rows

        # Insert attendees into the database
        if attendees_to_add:
            db.add_all(attendees_to_add)
            db.commit()

        return {"message": f"Successfully added {len(attendees_to_add)} attendees"}

    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Invalid file encoding. Please upload a UTF-8 encoded CSV file.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.post("/attendee/{event_id}/bulk-check-in")
def bulk_check_in_attendees(event_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), user: dict = Depends(token_required)):
    """
    Bulk check-in attendees for a given event using a CSV file containing emails.
    """
    try:
        # Check if event exists
        event = db.query(Event).filter(Event.event_id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        # Read and parse CSV
        contents = file.file.read().decode("utf-8")
        file.file.seek(0)
        csv_reader = csv.reader(StringIO(contents))

        # Validate headers
        headers = next(csv_reader, None)  # Read the header row
        expected_headers = ["email"]

        if not headers or headers != expected_headers:
            raise HTTPException(status_code=400, detail="Invalid CSV format. Expected headers: 'email'")

        updated_count = 0
        processed_emails = set()  # Track processed emails to avoid duplicates in the same batch

        # Batch update attendees
        for row in csv_reader:
            try:
                email = row[0].strip().lower()  # Normalize email input

                # Skip duplicate emails within the batch
                if email in processed_emails:
                    continue

                attendee = db.query(Attendee).filter(
                    Attendee.email == email, Attendee.event_id == event_id
                ).first()

                if attendee and not attendee.check_in_status:
                    attendee.check_in_status = True
                    updated_count += 1
                    processed_emails.add(email)  # Mark as processed

            except IndexError:
                continue  

        # Commit changes only if updates were made
        if updated_count > 0:
            db.commit()

        return {"message": f"Successfully checked in {updated_count} attendees"}

    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Invalid file encoding. Please upload a UTF-8 encoded CSV file.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
