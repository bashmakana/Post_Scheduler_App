import streamlit as st
from db import database, crud
from ui.components import success_alert, error_alert

def connected_accounts_page():
    st.title("Connected Accounts")
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    db_session = database.SessionLocal()
    user_id = st.session_state.get("user_id")
    if not user_id:
        error_alert("You must be logged in to view connected accounts.")
        return

    accounts = [acc for acc in crud.get_user_social_accounts(db_session, user_id) if acc.platform == "x"]
    if not accounts:
        st.info("No X account connected.")
    else:
        for acc in accounts:
            st.markdown(f"""
            <div style='border:1px solid #ddd; border-radius:8px; padding:16px; margin-bottom:12px;'>
                <strong>Platform:</strong> X<br>
                <strong>Access Token (truncated):</strong> {acc.access_token[:10]}...<br>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Disconnect X", key=f"disconnect_{acc.id}"):
                crud.delete_social_account(db_session, acc.id)
                success_alert(f"Disconnected X account.")
                st.rerun()
    db_session.close()
