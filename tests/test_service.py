from datetime import date

import pytest
from fastapi import HTTPException

import main
from app.models import Notification
from app.services import DeadlineService, DuplicateShallNotPass, trans
from app.storage import Storage


@pytest.fixture
def deadline_service():
    return DeadlineService()


@pytest.fixture
def storage(tmp_path):
    return Storage(path=str(tmp_path / "test_data.json"))


@pytest.fixture
def service(storage, deadline_service):
    return DuplicateShallNotPass(storage=storage, deadline_service=deadline_service)


@pytest.fixture
def api_service(tmp_path, monkeypatch):
    test_storage = Storage(path=str(tmp_path / "api_data.json"))
    test_service = DuplicateShallNotPass(
        storage=test_storage,
        deadline_service=DeadlineService(),
    )
    monkeypatch.setattr(main, "service", test_service)
    return test_service


def test_trans_converts_iso_string_to_date():
    assert trans("2026-04-01") == date(2026, 4, 1)


def test_calculate_deadline_skips_weekend(deadline_service):
    assert deadline_service.calculate_deadline(date(2026, 4, 1)) == date(2026, 4, 6)


def test_get_reminder_dates_counts_only_working_days(deadline_service):
    assert deadline_service.get_reminder_dates(date(2026, 4, 20)) == [
        date(2026, 4, 17),
        date(2026, 4, 15),
        date(2026, 4, 9),
        date(2026, 3, 31),
        date(2026, 3, 9),
    ]


def test_verification_new_item_rejects_duplicate():
    data = [
        {"employee_id": 12, "event_date": "2026-02-28", "event_type": "hiring"}
    ]
    new_item = {"employee_id": 12, "event_date": "2026-02-28", "event_type": "hiring"}

    assert DuplicateShallNotPass.verification_new_item(new_item, data) is False


def test_append_new_item_saves_notification(service, storage):
    item = {"employee_id": 10, "event_date": "2026-04-01", "event_type": "vacation"}

    service.append_new_item(item)

    assert storage.load_from_file() == [item]


def test_append_new_item_raises_value_error_for_duplicate(service):
    item = {"employee_id": 10, "event_date": "2026-04-01", "event_type": "vacation"}
    service.append_new_item(item)

    with pytest.raises(ValueError, match="Duplicate"):
        service.append_new_item(item)


def test_create_notification_endpoint_returns_ok(api_service):
    response = main.create_notification(
        Notification(employee_id=10, event_date="2026-04-01", event_type="vacation")
    )

    assert response == {"status": "ok"}
    assert api_service.storage.load_from_file() == [
        {"employee_id": 10, "event_date": "2026-04-01", "event_type": "vacation"}
    ]


def test_create_notification_endpoint_returns_409_for_duplicate(api_service):
    payload = Notification(employee_id=10, event_date="2026-04-01", event_type="vacation")
    main.create_notification(payload)

    with pytest.raises(HTTPException) as exc_info:
        main.create_notification(payload)

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Уведомление уже существует"


def test_get_notifications_endpoint_returns_reminders(api_service):
    main.create_notification(
        Notification(employee_id=10, event_date="2026-04-01", event_type="vacation")
    )

    response = main.get_notifications(employee_id=10)

    assert response.model_dump(mode="json") == {
        "reminders": [
            [
                "2026-04-03",
                "2026-04-01",
                "2026-03-26",
                "2026-03-17",
                "2026-02-20",
            ]
        ]
    }


def test_get_notifications_endpoint_returns_404_for_unknown_employee(api_service):
    with pytest.raises(HTTPException) as exc_info:
        main.get_notifications(employee_id=999)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Пользователь не найден"
