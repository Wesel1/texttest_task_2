import uvicorn
from fastapi import FastAPI, HTTPException

from storage import Storage
from models import Notification, Answer
from services import Duplicate_shall_not_pass, DeadlineService


app = FastAPI()

storage = Storage(path="data.json")
deadline_service = DeadlineService()
service = Duplicate_shall_not_pass(storage=storage, deadline_service=deadline_service)

@app.get('/')
def healthcheck():
    return {"status": "ok"}

@app.post("/notifications")
def create_notification(request: Notification):
    try:
        service.append_new_item(new_item=request.model_dump(mode="json"))
        return {"status": "ok"}
    except ValueError:
        raise HTTPException(status_code=409, detail="Уведомление уже существует")


@app.get("/notifications")
def get_notifications(employee_id: int):
    return Answer(reminders=service.get_reminders(employee_id=employee_id))


if __name__ == '__main__':
    uvicorn.run("main:app", reload=True)