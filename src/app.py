"""
Mini CRM — Entry point.
Loads data, renders layout, and routes to client management pages.
"""

import streamlit as st
from data import load_data
from assets import render_styles, render_sidebar, render_logo
from client_management import view_all_clients, add_client, delete_client

st.set_page_config(page_title="Mini CRM", page_icon="\U0001f49a", layout="wide")

# Navigation state
if "nav_page" not in st.session_state:
    st.session_state["nav_page"] = "View all clients"

if st.session_state.get("redirect_to_all"):
    st.session_state["nav_page"] = "View all clients"
    st.session_state["redirect_to_all"] = False

# Styles and layout
render_styles()

data = load_data()
clients = data["clients"]

page = render_sidebar()
render_logo()

# Route to page
if page == "View all clients":
    view_all_clients(clients, data)
elif page == "Add client":
    add_client(clients, data)
elif page == "Delete client":
    delete_client(clients, data)
