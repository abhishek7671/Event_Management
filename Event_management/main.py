from fastapi import FastAPI
from database import engine, Base
from routers import events, attendence, auth_routes


app = FastAPI(
    title="Event Management API",
    description="An API for managing events and attendees.",
    version="1.0.0",
    docs_url="/docs",  # Custom Swagger docs URL
    redoc_url="/redoc",  # Enable ReDoc UI
)

# Create database tables (ensure all models are initialized)
Base.metadata.create_all(bind=engine)


app.include_router(events.router, prefix="/events", tags=["Events"])
app.include_router(attendence.router, prefix="/attendees", tags=["Attendees"])
app.include_router(auth_routes.router, prefix="/auth_routes", tags=["auth_routes"])



