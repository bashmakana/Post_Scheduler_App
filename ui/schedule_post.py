import streamlit as st
from db import database, crud
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from ui.components import success_alert, error_alert
from scheduler import post_scheduler

# Create one scheduler for the app lifetime
if "scheduler" not in st.session_state:
    st.session_state.scheduler = BackgroundScheduler()
    st.session_state.scheduler.start()

def schedule_post_page():
    # Ensure scheduler is initialized in session state
    if "scheduler" not in st.session_state:
        from apscheduler.schedulers.background import BackgroundScheduler
        st.session_state.scheduler = BackgroundScheduler()
        st.session_state.scheduler.start()
    st.title("Schedule a Post")
    db_session = database.SessionLocal()
    user_id = st.session_state.get("user_id")


    if not user_id:
        error_alert("You must be logged in to schedule a post.")
        return

    # Check for connected X account
    connected_accounts = crud.get_user_social_accounts(db_session, user_id)
    x_connected = any(acc.platform == "x" for acc in connected_accounts)
    if not x_connected:
        error_alert("You must connect your X account before scheduling a post.")
        db_session.close()
        return

    st.markdown("### Platform: X (formerly Twitter)")
    platform = "x"
    content = st.text_area("Post Content", max_chars=280)
    uploaded_image = st.file_uploader("Upload Image (optional)", type=["jpg", "jpeg", "png", "gif"])

    # Set default time only on first load
    if "default_time" not in st.session_state:
        st.session_state.default_time = (datetime.now() + timedelta(hours=1)).time()

    date = st.date_input("Schedule Date", value=datetime.now().date())
    time = st.time_input("Schedule Time", value=st.session_state.default_time, step=120)
    scheduled_time = datetime.combine(date, time)
    print(f"scheduled time: {scheduled_time}")
    if st.button("Schedule Post"):
        if not content.strip() and not uploaded_image:
            error_alert("You must provide post content or upload an image.")
        elif scheduled_time <= datetime.now():
            error_alert("Scheduled time must be in the future.")
        else:
            # Save post to DB
            print("Saved post to db")
            post = crud.create_post(db_session, user_id, platform, content, scheduled_time)
            print("successfully created post, about to add job")

            # Save image to disk if uploaded
            image_path = None
            if uploaded_image:
                import os
                image_dir = "uploaded_images"
                os.makedirs(image_dir, exist_ok=True)
                image_path = os.path.join(image_dir, f"{post.id}_{uploaded_image.name}")
                with open(image_path, "wb") as f:
                    f.write(uploaded_image.read())

            # Schedule the posting job (pass the post object and image path)
            st.session_state.scheduler.add_job(
                post_scheduler.post_to_twitter,
                "date",
                run_date=scheduled_time,
                args=[post, db_session, image_path],
                id=f"post_{post.id}"
            )

            success_alert(f"Post scheduled for {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}!")


    db_session.close()
