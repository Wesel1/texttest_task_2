from pydantic import BaseModel

class Notification(BaseModel):
    employee_id: int
    event_date: str
    event_type: str

class Answer(BaseModel):
    reminders: list[list[str]]