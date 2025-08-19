import streamlit as st
from db import database
from sqlalchemy.orm import Session
from oauth_clients import twitter_oauth

def twitter_oauth_ui(current_user_id: int):
    st.title("Connect Twitter Account")

    db_session: Session = database.SessionLocal()

    # Check if user already has access tokens in session state
    access_token = st.session_state.get(twitter_oauth.ACCESS_TOKEN_KEY)
    access_token_secret = st.session_state.get(twitter_oauth.ACCESS_TOKEN_SECRET_KEY)

    if access_token and access_token_secret:
        st.success("Twitter account connected!")
        st.write(f"Access Token (truncated): {access_token[:10]}...")

        if st.button("Disconnect Twitter"):
            keys_to_clear = [
                twitter_oauth.ACCESS_TOKEN_KEY,
                twitter_oauth.ACCESS_TOKEN_SECRET_KEY,
                twitter_oauth.OAUTH_REQUEST_TOKEN_KEY,
                twitter_oauth.OAUTH_REQUEST_TOKEN_SECRET_KEY,
                twitter_oauth.OAUTH_VERIFIER_KEY,
            ]
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]

            # Remove X account from DB
            from db import crud
            accounts = crud.get_user_social_accounts(db_session, current_user_id)
            for acc in accounts:
                if acc.platform == "x":
                    crud.delete_social_account(db_session, acc.id)

            st.rerun()

    else:
        if st.button("Start Twitter OAuth Flow"):
            success, info = twitter_oauth.start_auth_flow()
            if not success:
                st.error(f"Failed to start OAuth flow: {info}")

        # Manual verifier input for local OAuth workaround
        st.write("If you see a code (verifier) in your browser after authorizing Twitter, copy and paste it below.")
        verifier_input = st.text_input("Paste Twitter verifier code here")
        if verifier_input:
            st.session_state[twitter_oauth.OAUTH_VERIFIER_KEY] = verifier_input
            if st.button("Complete Authentication"):
                success, info = twitter_oauth.complete_auth_flow(current_user_id, db_session)
                if success:
                    st.success("Twitter OAuth completed successfully!")
                else:
                    st.error(f"Failed to complete OAuth: {info}")

    db_session.close()
import streamlit as st
from oauth_clients import twitter_oauth