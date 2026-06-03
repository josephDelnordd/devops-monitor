import time
from datetime import datetime

import requests
import pandas as pd
import streamlit as st

# =====================
# Configuration
# =====================
API_URL = "http://localhost:8000"
API_KEY = "dev-secret-key"

REFRESH_METRICS = 2
REFRESH_SERVERS = 5

st.set_page_config(
    page_title="DevOps Monitoring Dashboard",
    page_icon="📊",
    layout="wide",
)

# =====================
# Helpers API
# =====================
@st.cache_data(ttl=REFRESH_METRICS)
def fetch_metrics():
    return requests.get(f"{API_URL}/metrics", timeout=3).json()


@st.cache_data(ttl=REFRESH_SERVERS)
def fetch_servers():
    return requests.get(f"{API_URL}/servers", timeout=3).json()


def post_server(payload: dict):
    return requests.post(
        f"{API_URL}/servers",
        headers={"X-API-Key": API_KEY},
        json=payload,
        timeout=3,
    )


def check_server(server_id: str):
    return requests.post(f"{API_URL}/servers/{server_id}/check", timeout=3)


# =====================
# Sidebar
# =====================
st.sidebar.title("⚙️ Configuration")
st.sidebar.markdown("Paramètres du dashboard")

auto_refresh = st.sidebar.toggle("🔄 Rafraîchissement auto", value=True)
max_points = st.sidebar.slider("Historique (points)", 30, 120, 60)

# =====================
# Tabs
# =====================
tab_metrics, tab_servers = st.tabs(["📊 Metrics", "🖥️ Servers"])

# =====================
# TAB 1 — METRICS
# =====================
with tab_metrics:
    metrics = fetch_metrics()

    # ---- KPIs
    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "CPU (%)",
        f"{metrics['cpu_percent']} %",
        delta="⚠️" if metrics["cpu_percent"] > 80 else None,
    )

    c2.metric(
        "Mémoire (%)",
        f"{metrics['memory_percent']} %",
        delta="⚠️" if metrics["memory_percent"] > 85 else None,
    )

    c3.metric(
        "Mémoire utilisée",
        f"{metrics['memory_used_gb']} GB",
    )

    c4.metric(
        "Disque (%)",
        f"{metrics['disk_percent']} %",
        delta="⚠️" if metrics["disk_percent"] > 90 else None,
    )

    st.divider()

    # ---- Historique
    if "metrics_history" not in st.session_state:
        st.session_state.metrics_history = []

    st.session_state.metrics_history.append(
        {
            "time": datetime.now().strftime("%H:%M:%S"),
            "cpu": metrics["cpu_percent"],
            "memory": metrics["memory_percent"],
        }
    )

    st.session_state.metrics_history = st.session_state.metrics_history[-max_points:]

    hist_df = pd.DataFrame(st.session_state.metrics_history)
    hist_df = hist_df.set_index("time")

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("CPU (%)")
        st.line_chart(hist_df["cpu"])

    with col_b:
        st.subheader("Memory (%)")
        st.line_chart(hist_df["memory"])

    # ---- Auto refresh
    if auto_refresh:
        time.sleep(REFRESH_METRICS)
        st.rerun()

# =====================
# TAB 2 — SERVERS
# =====================
with tab_servers:
    servers = fetch_servers()
    df = pd.DataFrame(servers)

    st.subheader("📋 Serveurs monitorés")

    if not df.empty:
        def status_color(val):
            if val == "UP":
                return "background-color: #c8f7c5"
            if val == "DEGRADED":
                return "background-color: #ffeaa7"
            if val == "DOWN":
                return "background-color: #fab1a0"
            return ""

        st.dataframe(
            df.style.applymap(status_color, subset=["status"]),
            use_container_width=True,
        )
    else:
        st.info("Aucun serveur enregistré.")

    st.divider()

    # ---- Actions
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("➕ Ajouter un serveur")
        with st.form("add_server", clear_on_submit=True):
            name = st.text_input("Nom")
            host = st.text_input("Host", value="localhost")
            port = st.number_input("Port", min_value=1, max_value=65535, value=8000)

            submitted = st.form_submit_button("Ajouter")

            if submitted:
                resp = post_server(
                    {"name": name, "host": host, "port": port}
                )
                if resp.status_code == 201:
                    st.success("Serveur ajouté")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("Erreur lors de l’ajout")

    with col2:
        st.subheader("🔍 Health check manuel")

        if not df.empty:
            server_id = st.selectbox(
                "Serveur",
                options=df["id"],
                format_func=lambda x: df[df["id"] == x]["name"].values[0],
            )

            if st.button("Lancer le check"):
                r = check_server(server_id)
                if r.status_code == 200:
                    st.success("Health check déclenché")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("Échec du health check")
