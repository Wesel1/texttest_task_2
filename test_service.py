from services import DeadlineService, Duplicate_shall_not_pass
import json

test_service_1 = DeadlineService()
test_service_2 = Duplicate_shall_not_pass("test_data.json")

data_always= [
  {
    "employee_id": 12,
    "event_date": "2026-01-01",
    "event_type": "skiing"
  },
  {
    "employee_id": 12,
    "event_date": "2026-02-28",
    "event_type": "hiring"
  }
]


try:
    with open("test_data.json", "r", encoding="utf-8") as f:
        test_data = json.load(f)
except FileNotFoundError:
    with open("test_data.json", "w", encoding="utf-8") as f:
        json.dump(data_always, f, ensure_ascii=False, indent=2)
    test_data = data_always


test_correct_input = {
        "employee_id": 10,
        "event_date": "2025-01-01",
        "event_type": "skiing"
}

test_incorrect_input = {
        "employee_id": 12,
        "event_date": "2026-02-28",
        "event_type": "hiring"
}

res = test_service_2.verification_new_item(test_correct_input, test_data)
assert res == True, f"Не получается создать нового несуществующего поля"

res = test_service_2.verification_new_item(test_incorrect_input, test_data)
assert res == False, f"Дозволяет записывать существующее поле"

test_data = "2025-05-07"
res = test_service_1.calculate_deadline(test_data)
assert res == "2025-05-14", f"Ожидалось - 2025-05-14, получилось - {res}"

try:
    test_service_2.append_new_item(test_incorrect_input)
except Exception as e:
    assert type(e) == ValueError, f"Ожидалось ValueError, а пришло {type(e)}"

res = test_service_2.find_event_date(12)
assert res == ["2026-01-01", "2026-02-28"], f"Найдены не все даты по id, найдено {res}"

with open("test_data.json", "w", encoding="utf-8") as f:
    json.dump(data_always, f, ensure_ascii=False, indent=2)


print("✅ Все тесты пройдены успешно! ✅")
