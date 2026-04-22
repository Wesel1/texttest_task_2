import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from services import Dublicate_shall_not_pass, DeadlineService

service_deadline = DeadlineService()
service_dub = Dublicate_shall_not_pass("data.json")

class Notification(BaseModel):
    employee_id: int
    event_date: str
    event_type: str

class Answer(BaseModel):
    reminders: list[list[str]]

app = FastAPI()

@app.get('/')
def home():
    return {"status": "ok"}

@app.post("/notifications")
def create_notification(request: Notification):
    new_item = request.model_dump(mode="json")
    try:
        service_dub.append_new_item(new_item=new_item)
        return {"status": "ok"}
    except ValueError:
        raise HTTPException(status_code=409, detail="Уведомление уже существует")


@app.get("/notifications")
def get_notifications(employee_id: int):
    all_reminders = []
    events = service_dub.find_event_date(employee_id=employee_id)
    for event in events:
        deadline = service_deadline.calculate_deadline(event_date=event)
        remind_dates = service_deadline.get_reminder_dates(deadline=deadline)
        all_reminders.append(remind_dates)
    return Answer(reminders=all_reminders)


if __name__ == '__main__':
    uvicorn.run("main:app", reload=True)