import streamlit as st
from datetime import datetime
import tweepy
from db import database, crud
from ui.components import post_card, info_alert, success_alert
from scheduler.post_scheduler import process_pending_posts

def view_posts_page():
    if st.button("Process Pending Posts", key="process_pending_btn"):
        process_pending_posts()
        st.success("Pending posts processed. Refresh to see status updates.")
    def fetch_x_engagement(post, account):
        if not post.x_post_id:
            return post
        try:
            client = tweepy.Client(
                consumer_key="wYJ7ysiCIq7dcgpUzIvrFWcA6",
                consumer_secret="2d4qtiQ6Q8oUbweNREX4cIpi0f2ITmSon82JAKDDFb5AHb9kx8",
                access_token=account.access_token,
                access_token_secret=account.access_token_secret
            )
            tweet = client.get_tweet(post.x_post_id, tweet_fields=["public_metrics"])
            if tweet and hasattr(tweet, 'data') and 'public_metrics' in tweet.data:
                metrics = tweet.data['public_metrics']
                post.likes = metrics.get('like_count', 0)
                post.reposts = metrics.get('retweet_count', 0)
                post.replies = metrics.get('reply_count', 0)
                db_session.commit()
        except Exception as e:
            print(f"Error fetching engagement for post {post.id}: {e}")
        return post
    st.title("Your Scheduled & Posted Content")
    db_session = database.SessionLocal()
    user_id = st.session_state.get("user_id")
    id = st.session_state.get("id")
    if not user_id:
        info_alert("Log in to view your posts.")
        return
    posts = crud.get_user_posts(db_session, user_id)
    # Get X account for engagement API
    account = db_session.query(crud.models.SocialAccount).filter_by(user_id=user_id, platform="x").first()
    if not posts:
        info_alert("No posts found.")
    else:
        for post in posts:
            post = fetch_x_engagement(post, account) if post.x_post_id and account else post
            post_card(post)
            if st.button("Delete Schedule", key=f"delete this scheduled post {post.id}"):
                crud.delete_scheduled_post(db_session, post.id)
                # Remove scheduled job if it exists
                try:
                    st.session_state.scheduler.remove_job(f"post_{post.id}")
                except Exception:
                    pass
                success_alert("You have successfully deleted the scheduled post")
                st.rerun()
    db_session.close()
