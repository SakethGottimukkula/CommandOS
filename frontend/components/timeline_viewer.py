import streamlit as st

def show_timeline(logs):
    st.subheader("🖥 Basic Timeline")

    if not logs:
        st.info("Timeline empty!")
        return

    for entry in reversed(logs):
        st.write(f"[{entry.get('timestamp','')}] {entry.get('agent','')} → {entry.get('message','')}")
