import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "clients.json")

VALID_STATUSES = ["interested", "student", "client"]


def default_data():
    return {"next_id": 1, "clients": []}


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return default_data()


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def reorganize_ids(data):
    data["clients"].sort(key=lambda c: c["name"].lower())
    for i, client in enumerate(data["clients"], 1):
        client["id"] = i
    data["next_id"] = len(data["clients"]) + 1


def find_client_by_id(clients, client_id):
    for client in clients:
        if client["id"] == client_id:
            return client
    return None
