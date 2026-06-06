from pydantic import BaseModel
from datetime import date

class Notification(BaseModel):
    employee_id: int
    event_date: date
    event_type: str

class Answer(BaseModel):
    reminders: list[list[date]]