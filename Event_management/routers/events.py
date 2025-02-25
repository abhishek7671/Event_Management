from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db, SessionLocal
from models import Event, EventStatus
from schemas import EventCreate, EventUpdate, EventResponse
from auth import token_required

router = APIRouter()

@router.post("/", response_model=EventResponse)
def create_event(event: EventCreate, db: Session = Depends(get_db), user: dict = Depends(token_required) ):
    try:
        new_event = Event(**event.dict())
        db.add(new_event)
        db.commit()
        db.refresh(new_event)
        return new_event
    except ValueError as ve:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Invalid data: {str(ve)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.put("/{event_id}", response_model=EventResponse)
def update_event(event_id: int, event_update: EventUpdate, db: Session = Depends(get_db), user: dict = Depends(token_required)):
    try:
        event = db.query(Event).filter(Event.event_id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        for key, value in event_update.dict(exclude_unset=True).items():
            setattr(event, key, value)

        db.commit()
        db.refresh(event)
        return event
    except ValueError as ve:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Invalid data: {str(ve)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.get("/", response_model=list[EventResponse])
def list_events(status: EventStatus = None, location: str = None, db: Session = Depends(get_db), user: dict = Depends(token_required)):
    try:
        query = db.query(Event)
        
        if status:
            query = query.filter(Event.status == status)
        if location:
            query = query.filter(Event.location == location)

        events = query.all()
        
        if not events:
            raise HTTPException(status_code=404, detail="No events found matching the criteria")

        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

