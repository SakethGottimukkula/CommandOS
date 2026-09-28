import streamlit as st
import requests
import json
import os

# Load custom CSS
with open("styles/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


st.set_page_config(
    page_title="Saketh CommandOS",
    layout="wide"
)

API_URL = "http://localhost:8000"


# ========== Sidebar Memory Viewer ==========
def show_memory(user_id):
    st.sidebar.title("📦 Memory Viewer")
    try:
        res = requests.get(f"{API_URL}/memory/{user_id}")
        if res.status_code == 200:
            data = res.json()
            st.sidebar.json(data)
        else:
            st.sidebar.error("Failed to fetch memory!")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")


# ========== Command Center ==========
st.title("🧠 Saketh CommandOS")

user_id = st.text_input("User ID", value="saketh")

command = st.text_input("Enter Command (e.g. study:explain arrays)")

if st.button("Run Command"):
    try:
        payload = {"user_id": user_id, "command": command, "params": {}}
        res = requests.post(f"{API_URL}/command", json=payload)
        st.write(res.json())
    except Exception as e:
        st.error(f"Error: {e}")


st.markdown("---")


# ========== PDF Generator UI ==========
st.header("📄 PDF Report Generator")

report_type = st.selectbox("Report Type", ["study", "task", "content"])
summary = st.text_input("Summary")
details = st.text_area("Details")

if st.button("Generate PDF"):
    try:
        payload = {
            "report_type": report_type,
            "summary": summary,
            "details": details
        }
        res = requests.post(f"{API_URL}/pdf/create", json=payload)
        output = res.json()
        st.write(output)

        if "path" in output:
            with open(output["path"], "rb") as f:
                st.download_button(
                    label="⬇ Download PDF",
                    data=f,
                    file_name=os.path.basename(output["path"])
                )
    except Exception as e:
        st.error(f"Error: {e}")

st.markdown("---")


# ========== Neon Terminal Timeline ==========
st.header("🖥 Agent Communication Terminal")
try:
    res = requests.get(f"{API_URL}/memory/{user_id}")
    if res.status_code == 200:
        mem = res.json()
        logs = mem.get("history", [])
        from components.timeline_viewer import show_timeline
        show_timeline(logs)
    else:
        st.error("Failed to load timeline logs.")
except Exception as e:
    st.error(f"Timeline error: {e}")


# Show memory in sidebar
show_memory(user_id)
