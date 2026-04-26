import uvicorn
from fastapi import FastAPI, HTTPException

from storage import Storage
from models import Notification, Answer
from services import DuplicateShallNotPass, DeadlineService


app = FastAPI()

storage = Storage(path="data.json")
deadline_service = DeadlineService()
service = DuplicateShallNotPass(storage=storage, deadline_service=deadline_service)


@app.post("/notifications")
def create_notification(request: Notification):
    try:
        service.append_new_item(new_item=request.model_dump(mode="json"))
        return {"status": "ok"}
    except ValueError:
        raise HTTPException(status_code=409, detail="Уведомление уже существует")


@app.get("/notifications")
def get_notifications(employee_id: int):
    answer = service.get_reminders(employee_id=employee_id)
    if answer:
        return Answer(reminders=answer)
    else:
        raise HTTPException(status_code=404, detail="Пользователь не найден")


if __name__ == '__main__':
    uvicorn.run("main:app", reload=True)