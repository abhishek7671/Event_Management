from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional
import enum

class EventStatus(str, enum.Enum):
    scheduled = "scheduled"
    ongoing = "ongoing"
    completed = "completed"
    canceled = "canceled"

class EventBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: str
    max_attendees: int

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    max_attendees: Optional[int] = None
    status: Optional[EventStatus] = None

class EventResponse(EventBase):
    event_id: int
    status: EventStatus
    class Config:
        from_attributes = True

class AttendeeBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    event_id: int

class AttendeeCreate(AttendeeBase):
    pass

class AttendeeResponse(AttendeeBase):
    attendee_id: int
    check_in_status: bool
    class Config:
        from_attributes = True



class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    email: str
    password: str