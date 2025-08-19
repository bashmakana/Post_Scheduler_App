import streamlit as st
from db.database import get_db
from auth.auth import create_user, authenticate_user, get_user_by_username, get_user_by_email


def login_page():
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Log In"):
        if not username or not password:
            st.error("Please enter both username and password.")
            return

        db = next(get_db())
        user = authenticate_user(db, username, password)
        if user:
            st.session_state["user_id"] = user.id
            st.session_state["username"] = user.username
            st.success(f"Welcome back, {username}!")
            st.rerun()
        else:
            st.error("Invalid username or password")


def signup_page():
    st.title("📝 Sign Up")

    username = st.text_input("Choose a username")
    email = st.text_input("Email")
    password = st.text_input("Choose a password", type="password")
    password_confirm = st.text_input("Confirm password", type="password")

    if st.button("Sign Up"):
        if password != password_confirm:
            st.error("Passwords do not match")
            return

        db = next(get_db())
        if get_user_by_username(db, username):
            st.error("Username already taken")
            return
        if get_user_by_email(db, email):
            st.error("Email already registered")
            return
        create_user(db, username, email, password)
        st.success("Account created! Please log in.")


def logout():
    """Clear login session"""
    if "user_id" in st.session_state:
        st.session_state.clear()
    st.success("Logged out")


def auth_flow():
    """
    Handles auth state: 
    If not logged in → show Login/Sign Up selector
    If logged in → show 'logged in' state with logout
    """
    if "user_id" not in st.session_state:
        st.markdown("""
            <div style='text-align:center; margin-top:40px;'>
                <h1 style='color:#1DA1F2; font-size:2.5rem; font-weight:700;'>X Post Scheduler</h1>
                <p style='color:#555; font-size:1.2rem;'>Schedule your X posts, track engagement, and manage accounts easily.</p>
            </div>
        """, unsafe_allow_html=True)

        tabs = st.tabs(["Login", "Sign Up"])

        with tabs[0]:
            login_page()

        with tabs[1]:
            signup_page()
    else:
        st.success(f"Logged in as {st.session_state['username']}")
        if st.button("Log Out"):
            logout()
            st.rerun()
