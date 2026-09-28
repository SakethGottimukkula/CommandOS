import streamlit as st

def show_logs(logs):
    st.subheader("🧾 Agent Log Viewer")

    if not logs:
        st.info("No logs yet!")
        return

    for entry in logs:
        agent = entry.get("agent", "unknown").upper()
        message = entry.get("message", "")
        ts = entry.get("timestamp", "")

        st.markdown(f"""
        <div style='padding:10px; margin:5px; border-radius:8px; background:#1b1b1b;'>
            <b>[{ts}] {agent}</b><br>
            {message}
        </div>
        """, unsafe_allow_html=True)
