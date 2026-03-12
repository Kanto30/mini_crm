import streamlit as st
import pandas as pd
from datetime import datetime
from data import (
    load_data,
    save_data,
    reorganize_ids,
    find_client_by_id,
    VALID_STATUSES,
)

st.set_page_config(page_title="Mini CRM", page_icon="\U0001f49a", layout="wide")

STATUS_COLORS = {
    "interested": "#F0AD4E",
    "student": "#5BC0DE",
    "client": "#5CB85C",
}


def styled_status(status):
    color = STATUS_COLORS.get(status, "#FFFFFF")
    return f'<span style="color:{color}; font-weight:bold;">{status}</span>'


def client_selector(clients, key="client_select"):
    sorted_clients = sorted(clients, key=lambda c: c["name"].lower())
    options = [f"ID {c['id']} — {c['name']}" for c in sorted_clients]
    if not options:
        st.info("No clients available.")
        return None
    selection = st.selectbox("Select a client", options, key=key)
    selected_id = int(selection.split(" ")[1])
    return find_client_by_id(clients, selected_id)


# ── Navigation state helpers ──────────────────────────────────────────────────

if "nav_page" not in st.session_state:
    st.session_state["nav_page"] = "View all clients"

if st.session_state.get("redirect_to_all"):
    # This flag is set after adding a client; handle it BEFORE rendering sidebar.
    st.session_state["nav_page"] = "View all clients"
    st.session_state["redirect_to_all"] = False


def parse_notes_text(notes_text: str):
    """Convert the multiline Notes string back into a list of note dicts."""
    notes = []
    for line in notes_text.splitlines():
        line = line.strip()
        if not line:
            continue
        # Expect format "YYYY-MM-DD HH:MM: text"
        if len(line) > 18 and line[16:18] == ": ":
            date_part = line[:16]
            text_part = line[18:]
            notes.append({"date": date_part, "text": text_part})
        else:
            notes.append(
                {
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "text": line,
                }
            )
    return notes


def show_clients_table(clients):
    if not clients:
        st.info("No clients to display.")
        return
    sorted_clients = sorted(clients, key=lambda c: c["name"].lower())
    df = pd.DataFrame(
        [
            {
                "ID": c["id"],
                "Name": c["name"],
                "Phone": c["phone"],
                "Status": c["status"],
                "Notes": "\n".join(
                    f"{n['date']}: {n['text']}" for n in c.get("notes", [])
                ),
            }
            for c in sorted_clients
        ]
    )

    def color_status(val):
        color = STATUS_COLORS.get(val, "#FFFFFF")
        return f"color: {color}; font-weight: bold"

    styled_df = df.style.applymap(color_status, subset=["Status"])
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
    st.caption(f"Total: **{len(sorted_clients)}** client(s)")


# ── Sidebar ──────────────────────────────────────────────────────────────────

st.sidebar.markdown("## \U0001f49a Mini CRM")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    [
        "View all clients",
        "Add client",
        "Delete client",
    ],
    key="nav_page",
)

st.sidebar.markdown("---")
st.sidebar.caption("Wellness Client Manager")


# ── Load data ────────────────────────────────────────────────────────────────

data = load_data()
clients = data["clients"]


# ── Pages ────────────────────────────────────────────────────────────────────

if page == "View all clients":
    st.title("All Clients")
    if not clients:
        st.info("No clients to display.")
    else:
        # Build editable table with full notes content
        sorted_clients = sorted(clients, key=lambda c: c["name"].lower())
        rows = []
        for c in sorted_clients:
            notes_text = "\n".join(
                f"{n['date']}: {n['text']}" for n in c.get("notes", [])
            )
            rows.append(
                {
                    "ID": c["id"],
                    "Name": c["name"],
                    "Phone": c["phone"],
                    "Status": c["status"],
                    "Notes": notes_text,
                }
            )

        df = pd.DataFrame(rows)

        edited_df = st.data_editor(
            df,
            column_config={
                "ID": st.column_config.NumberColumn(disabled=True),
                "Phone": st.column_config.TextColumn(),
                "Notes": st.column_config.TextColumn(),
                "Status": st.column_config.SelectboxColumn(
                    options=VALID_STATUSES
                ),
            },
            hide_index=True,
            use_container_width=True,
            key="clients_editor",
        )

        # Apply inline edits for Name and Status
        id_to_client = {c["id"]: c for c in clients}
        any_change = False
        name_changed = False

        for _, row in edited_df.iterrows():
            client_id = int(row["ID"])
            client = id_to_client.get(client_id)
            if not client:
                continue

            new_name = str(row["Name"]).strip()
            new_status = str(row["Status"]).strip()
            new_phone = str(row["Phone"]).strip()
            new_notes_raw = str(row["Notes"]).strip()

            if new_name and new_name != client["name"]:
                client["name"] = new_name
                any_change = True
                name_changed = True

            if (
                new_status
                and new_status in VALID_STATUSES
                and new_status != client["status"]
            ):
                client["status"] = new_status
                any_change = True

            if new_phone and new_phone != client["phone"]:
                client["phone"] = new_phone
                any_change = True

            original_notes_text = "\n".join(
                f"{n['date']}: {n['text']}" for n in client.get("notes", [])
            )
            if new_notes_raw != original_notes_text:
                client["notes"] = parse_notes_text(new_notes_raw)
                any_change = True

        if any_change:
            if name_changed:
                reorganize_ids(data)
            save_data(data)
            st.success("Saved")

        st.caption(
            "Tip: click a cell in the Name or Status column to edit it directly."
        )

elif page == "Add client":
    st.title("Add New Client")

    with st.form("add_client_form", clear_on_submit=True):
        name = st.text_input("Name")
        phone = st.text_input("Phone")
        submitted = st.form_submit_button("Add client")

    if submitted:
        if not name.strip() or not phone.strip():
            st.error("Name and phone cannot be empty.")
        else:
            clients.append({
                "id": 0,
                "name": name.strip(),
                "phone": phone.strip(),
                "status": "interested",
                "notes": [],
            })
            reorganize_ids(data)
            save_data(data)
            st.success("Saved")
            st.session_state["redirect_to_all"] = True
            st.rerun()

elif page == "Delete client":
    st.title("Delete Client")

    if not clients:
        st.info("No clients yet.")
    else:
        client = client_selector(clients, key="delete_select")
        if client:
            st.warning(
                f"You are about to delete **{client['name']}** "
                f"(Phone: {client['phone']}, Status: {client['status']})."
            )
            confirm = st.checkbox("I am sure I want to delete this client")

            if st.button("Delete client"):
                if not confirm:
                    st.error("Please check the confirmation box first.")
                else:
                    name = client["name"]
                    data["clients"].remove(client)
                    reorganize_ids(data)
                    save_data(data)
                    st.success(f"Client deleted: **{name}**")
                    st.rerun()
