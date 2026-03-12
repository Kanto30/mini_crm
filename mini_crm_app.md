### Streamlit Mini CRM — Plan

#### Overview

- **Goal**: Keep the current terminal-based Mini CRM and add a **Streamlit web interface**.
- **Language**: Python.
- **Data**: Continue using the existing `clients.json` file.
- **Architecture**: Share core logic between the terminal app and the web app.

---

### Step 1 — Install Streamlit

In the terminal (inside the `mini_crm` folder):

```bash
pip install streamlit
```

---

### Step 2 — Create `data.py` (shared logic)

1. Create a new file called `data.py`.
2. Move these functions from `crm.py` into `data.py`:

   - `default_data()`
   - `load_data()`
   - `save_data()`
   - `reorganize_ids()`
   - `find_client_by_id()`

3. In `data.py`, keep the same implementations they currently have in `crm.py`.
4. In `crm.py`, remove the old definitions and import them instead:

   ```python
   from data import (
       default_data,
       load_data,
       save_data,
       reorganize_ids,
       find_client_by_id,
   )
   ```

5. Run the terminal CRM:

```bash
python crm.py
```

to make sure everything still works.

---

### Step 3 — Create `app.py` (Streamlit entry point)

1. Create a new file called `app.py`.
2. Add the basic skeleton:

```python
import streamlit as st
from data import load_data, save_data, reorganize_ids, find_client_by_id
from datetime import datetime

st.set_page_config(page_title="Mini CRM", page_icon="💚", layout="wide")
```

3. Add sidebar navigation:

```python
page = st.sidebar.selectbox(
   "Go to",
   [
       "View all clients",
       "Add client",
       "Change status",
       "Add note",
       "Edit client",
       "Delete client",
       "Search by status",
   ],
)
```

4. Load data at the top:

```python
data = load_data()
clients = data["clients"]
```

---

### Step 4 — Implement “View all clients” page

When `page == "View all clients"`:

1. Sort `clients` alphabetically by name.
2. Build a structure for display, for example:

```python
import pandas as pd

df = pd.DataFrame([
   {
       "ID": c["id"],
       "Name": c["name"],
       "Phone": c["phone"],
       "Status": c["status"],
   }
   for c in sorted(clients, key=lambda c: c["name"].lower())
])
```

3. Show the table:

```python
st.subheader("All clients")
st.table(df)
```

4. Optionally, style the status column using colors (for example with `st.markdown` or styling helpers).

---

### Step 5 — Implement “Add client” page

When `page == "Add client"`:

1. Create form inputs:

```python
name = st.text_input("Name")
phone = st.text_input("Phone")
```

2. Handle button click:

```python
if st.button("Add client"):
   if not name or not phone:
       st.error("Name and phone cannot be empty.")
   else:
       clients = data["clients"]
       clients.append({
           "id": 0,  # will be set by reorganize_ids
           "name": name,
           "phone": phone,
           "status": "interested",
           "notes": [],
       })
       reorganize_ids(data)
       save_data(data)
       st.success(f"Client added: {name}")
```

---

### Step 6 — Implement “Change status” page

When `page == "Change status"`:

1. Build a list of options for selection:

```python
options = [
   f"ID {c['id']} — {c['name']}"
   for c in sorted(clients, key=lambda c: c["name"].lower())
]
selection = st.selectbox("Select a client", options) if options else None
```

2. Extract the selected client based on the chosen option.
3. Provide a status dropdown:

```python
statuses = ["interested", "student", "client"]
new_status = st.selectbox("New status", statuses)
```

4. On button click:

```python
if st.button("Update status"):
   # find and update the client
   save_data(data)
   st.success("Status updated.")
```

---

### Step 7 — Implement “Add note” page

When `page == "Add note"`:

1. Select a client as in Step 6.
2. Show existing notes (if any):

```python
if client["notes"]:
   st.subheader(f"Notes for {client['name']}")
   for n in client["notes"]:
       st.write(f"{n['date']}: {n['text']}")
else:
   st.info("No notes yet for this client.")
```

3. Provide a text area and button:

```python
note_text = st.text_area("New note")
if st.button("Add note"):
   if not note_text.strip():
       st.error("Note cannot be empty.")
   else:
       client["notes"].append({
           "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
           "text": note_text.strip(),
       })
       save_data(data)
       st.success("Note added.")
```

---

### Step 8 — Implement “Edit client” page

When `page == "Edit client"`:

1. Select a client.
2. Pre-fill editable fields:

```python
new_name = st.text_input("Name", value=client["name"])
new_phone = st.text_input("Phone", value=client["phone"])
```

3. On button click:

```python
if st.button("Save changes"):
   if not new_name or not new_phone:
       st.error("Name and phone cannot be empty.")
   else:
       client["name"] = new_name
       client["phone"] = new_phone
       reorganize_ids(data)
       save_data(data)
       st.success("Client updated.")
```

---

### Step 9 — Implement “Delete client” page

When `page == "Delete client"`:

1. Select a client.
2. Add a confirmation checkbox:

```python
confirm = st.checkbox("I am sure I want to delete this client")
```

3. On button click:

```python
if st.button("Delete client"):
   if not confirm:
       st.error("Please confirm deletion.")
   else:
       data["clients"].remove(client)
       reorganize_ids(data)
       save_data(data)
       st.success("Client deleted.")
```

---

### Step 10 — Implement “Search by status” page

When `page == "Search by status"`:

1. Let user choose a status:

```python
status = st.selectbox("Status", ["interested", "student", "client"])
```

2. Filter clients:

```python
filtered = [
   c for c in clients
   if c["status"] == status
]
```

3. Show filtered list in a table as in Step 4.

---

### Step 11 — Test both versions

**Terminal version:**

```bash
python crm.py
```

- Test add, view, edit, delete, status, notes, search.

**Streamlit version:**

```bash
streamlit run app.py
```

- Test:
   - View all clients
   - Add client
   - Change status
   - Add note
   - Edit client
   - Delete client
   - Search by status

Confirm that both use the same `clients.json` and changes in one are visible in the other.

---

### Step 12 — Save to GitHub

In the terminal:

```bash
git add .
git commit -m "Add Streamlit web interface for Mini CRM"
git push
```

You will now have:

- **Terminal CRM**: `python crm.py`
- **Web CRM**: `streamlit run app.py`

Both sharing the same data and logic, with two ways to interact with your wellness client system.
