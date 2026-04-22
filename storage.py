import json

class Storage:
    def __init__(self, path: str):
        self.path = path

    def load_to_file(self) -> list:
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = []
        return data

    def save_to_file(self, data: list) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)