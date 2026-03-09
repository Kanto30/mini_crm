import json
import os
from datetime import datetime

DATA_FILE = "clients.json"

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


def find_client_by_id(clients, client_id):
    for client in clients:
        if client["id"] == client_id:
            return client
    return None


def add_client(data):
    print("\n--- Add New Client ---")

    name = input("Name: ").strip()
    if not name:
        print("[!] Name cannot be empty.")
        return

    phone = input("Phone: ").strip()
    if not phone:
        print("[!] Phone cannot be empty.")
        return

    client = {
        "id": data["next_id"],
        "name": name,
        "phone": phone,
        "status": "interested",
        "notes": []
    }

    data["clients"].append(client)
    data["next_id"] += 1
    save_data(data)
    print(f"[+] Client added: {name} (ID: {client['id']})")
