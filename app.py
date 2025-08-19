import streamlit as st
from ui import login
from ui import connect_accounts

def main():
    st.title("X Post Scheduler App")

    if "user_id" not in st.session_state:
        login.auth_flow()
    else:
        user_id = st.session_state["user_id"]

        from ui.schedule_post import schedule_post_page
        from ui.view_posts import view_posts_page
        from ui.connected_accounts import connected_accounts_page


        st.title("Welcome to X Post Scheduler App")
        st.markdown("<hr>", unsafe_allow_html=True)
        st.write("Select an action:")


        # Add logout button at the top right
        _, logout_col = st.columns([5, 1])
        with logout_col:
            if st.button("🚪 Log Out", key="logout_btn", use_container_width=True):
                from ui.login import logout
                logout()
                st.session_state.clear()
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        nav_cols = st.columns(2)
        with nav_cols[0]:
            if st.button("🔗 Connect Accounts", key="connect_accounts_btn", help="Connect your social accounts", use_container_width=True):
                st.session_state["page"] = "connect_accounts"
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("📋 View Posts", key="view_posts_btn", help="View your scheduled and posted content", use_container_width=True):
                st.session_state["page"] = "view_posts"
        with nav_cols[1]:
            if st.button("✅ Connected Accounts", key="connected_accounts_btn", help="See your connected accounts", use_container_width=True):
                st.session_state["page"] = "connected_accounts"
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("📝 Schedule Post", key="schedule_post_btn", help="Schedule a new post", use_container_width=True):
                st.session_state["page"] = "schedule_post"

        # Show selected page in main area
        page = st.session_state.get("page")
        if page == "connect_accounts":
            connect_accounts.twitter_oauth_ui(user_id)
        elif page == "connected_accounts":
            connected_accounts_page()
        elif page == "schedule_post":
            schedule_post_page()
        elif page == "view_posts":
            view_posts_page()

if __name__ == "__main__":
    main()
