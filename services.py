from datetime import datetime, timedelta, date
import holidays

from storage import Storage

def trans(a: str) -> date:
    return datetime.fromisoformat(a).date()

class DeadlineService():
    def __init__(self):
        self.ru_holidays = holidays.Russia()
        self.tuple_reminders = (1, 3, 7, 14, 30)

    def calculate_deadline(self, event_date: date) -> date:
        deadline = event_date
        i = 0
        while i < 3:
            deadline += timedelta(days=1)
            if not self.wrong_day(deadline):
                i += 1
        return deadline


    def get_reminder_dates(self, deadline: date) -> list[date]:
        date_reminders = []
        for i in self.tuple_reminders:
            deadline_copy = deadline
            count = 0
            while count < i:
                deadline_copy -= timedelta(days=1)
                if not self.wrong_day(deadline_copy):
                    count += 1
            date_reminders.append(deadline_copy)
        return date_reminders


    def wrong_day(self, day: date) -> True | False:
        is_holiday = day in self.ru_holidays
        is_weekend = day.weekday() > 4

        return is_holiday or is_weekend


class DuplicateShallNotPass():
    def __init__(self, storage: Storage, deadline_service: DeadlineService):
        self.storage = storage
        self.deadline_service = deadline_service

    @staticmethod
    def verification_new_item(new_item: dict, data: list) -> bool:
        for i in data:
            if (
                i["employee_id"] == new_item["employee_id"]
                and i["event_date"] == new_item["event_date"]
                and i["event_type"] == new_item["event_type"]
            ):
                return False
        return True

    def append_new_item(self, new_item: dict) -> None:
        data = self.storage.load_to_file()

        if self.verification_new_item(new_item, data):
            data.append(new_item)
            self.storage.save_to_file(data)
        else:
            raise ValueError("Duplicate")


    def get_reminders(self, employee_id: int) -> list:
        all_reminders = []
        data = self.storage.load_to_file()
        events = [i['event_date'] for i in data if i['employee_id'] == employee_id]
        for event in events:
            deadline = self.deadline_service.calculate_deadline(event_date=trans(event))
            remind_dates = self.deadline_service.get_reminder_dates(deadline=deadline)
            all_reminders.append(remind_dates)
        return all_reminders
