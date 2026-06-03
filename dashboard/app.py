import time
import requests
import streamlit as st
import pandas as pd

API_URL = "http://localhost:8000"
API_KEY = "dev-secret-key"

st.set_page_config(layout="wide")
tabs = st.tabs(["📊 Metrics", "🖥️ Servers"])

@st.cache_data(ttl=2)
def fetch_metrics():
    return requests.get(f"{API_URL}/metrics").json()

@st.cache_data(ttl=5)
def fetch_servers():
    return requests.get(f"{API_URL}/servers").json()

with tabs[0]:
    metrics = fetch_metrics()
    col1, col2, col3 = st.columns(3)

    col1.metric("CPU %", metrics["cpu_percent"])
    col2.metric("Memory %", metrics["memory_percent"])
    col3.metric("Disk %", metrics["disk_percent"])

    if "history" not in st.session_state:
        st.session_state.history = []

    st.session_state.history.append({
        "cpu": metrics["cpu_percent"],
        "memory": metrics["memory_percent"]
    })

    st.session_state.history = st.session_state.history[-60:]
    df = pd.DataFrame(st.session_state.history)

    st.line_chart(df)
    time.sleep(2)
    st.rerun()

with tabs[1]:
    servers = fetch_servers()
    df = pd.DataFrame(servers)

    if not df.empty:
        st.dataframe(df)

    with st.form("add_server"):
        name = st.text_input("Name")
        host = st.text_input("Host")
        port = st.number_input("Port", min_value=1, max_value=65535)
        submitted = st.form_submit_button("Add server")

        if submitted:
            requests.post(
                f"{API_URL}/servers",
                headers={"X-API-Key": API_KEY},
                json={"name": name, "host": host, "port": port},
            )
            st.rerun()