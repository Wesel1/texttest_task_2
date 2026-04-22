import json

from datetime import datetime, timedelta, date
import holidays


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


class Dublicate_shall_not_pass():
    def __init__(self, path_to_file: str):
        self.path_to_file = path_to_file

    def open_data_read(self) -> list:
        try:
            with open(self.path_to_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = []
        return data

    def open_data_write(self, data: list) -> None:
        with open(self.path_to_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

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
        data = self.open_data_read()

        if self.verification_new_item(new_item, data):
            data.append(new_item)
            self.open_data_write(data)
        else:
            raise ValueError("Duplicate")


    def find_event_date(self, employee_id: int) -> list:
        data = self.open_data_read()
        event_dates = [i['event_date'] for i in data if i['employee_id'] == employee_id]
        return event_dates

if __name__ == '__main__':
    service = Dublicate_shall_not_pass("data.json")
    pa = service.find_event_date(10)
    print(pa)


# получаем уведомление -> открываем бд для чтения -> считываем всю информацию от туда ->
# -> сравниваем инфу из бд с уведомлением -> открываем бд для записи -> перезаписываем
#                                         -> вызываем ошибку


















