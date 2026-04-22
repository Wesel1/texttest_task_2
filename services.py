from datetime import datetime, timedelta, date
import holidays

from storage import Storage


class DeadlineService():
    def __init__(self):
        self.ru_holidays = holidays.Russia()

    def calculate_deadline(self, event_date: str) -> str:
        deadline = datetime.fromisoformat(event_date).date()
        i = 0
        while i < 3:
            deadline += timedelta(days=1)
            if not self.wrong_day(deadline):
                i += 1
        return str(deadline)


    def get_reminder_dates(self, deadline: str) -> list[str]:
        date_reminders = []
        tuple_reminders = (1, 3, 7, 14, 30)
        for i in tuple_reminders:
            deadline_copy = datetime.fromisoformat(deadline).date()
            count = 0
            while count < i:
                deadline_copy -= timedelta(days=1)
                if not self.wrong_day(deadline_copy):
                    count += 1
            date_reminders.append(str(deadline_copy))
        return date_reminders


    def wrong_day(self, day: date) -> True | False:
        is_holiday = day in self.ru_holidays
        is_weekend = day.weekday() > 4

        return is_holiday or is_weekend


class Duplicate_shall_not_pass():
    def __init__(self, storage: Storage, deadline_service: DeadlineService):
        self.storage = storage
        self.deadline_service = deadline_service

    def verification_new_item(self, new_item: dict, data: list) -> bool:
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
            deadline = self.deadline_service.calculate_deadline(event_date=event)
            remind_dates = self.deadline_service.get_reminder_dates(deadline=deadline)
            all_reminders.append(remind_dates)
        return all_reminders

if __name__ == '__main__':
    storage = Storage("data.json")
    service_1 = DeadlineService()
    service = Duplicate_shall_not_pass(storage, service_1)
    test = {"employee_id": 12, "event_date": "2025-02-28", "event_type": "hiring"}
    service.append_new_item(test)
    print(service.get_reminders(10))


# получаем уведомление -> открываем бд для чтения -> считываем всю информацию от туда ->
# -> сравниваем инфу из бд с уведомлением -> открываем бд для записи -> перезаписываем
#                                         -> вызываем ошибку


















