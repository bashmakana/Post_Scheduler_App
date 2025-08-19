import time
from apscheduler.schedulers.background import BackgroundScheduler
from db import database, crud
from datetime import datetime
import tweepy
from oauth_clients import twitter_oauth
import requests

def post_to_twitter(post, db_session, image_path=None):
    print("Retrieving user's access")
    account = db_session.query(crud.models.SocialAccount)\
        .filter_by(user_id=post.user_id, platform="x")\
        .first()

    if not account or not account.access_token or not account.access_token_secret:
        return False, "No valid Twitter credentials stored."

    import socket
    try:
        print("Here now (v2)")
        client = tweepy.Client(
            consumer_key="3N5NbdWUwER3iVNAqOTbejczJ",
            consumer_secret="FrqJnF7Nz9MNpVFzbZLkS4NHYwfi5Rjv7DAh2bzVbnkRcdvekq",
            access_token=account.access_token,
            access_token_secret=account.access_token_secret
        )
        print("Client created ✅")
        media_ids = None
        # If image_path is provided, upload media
        if image_path:
            try:
                api_v1 = tweepy.API(twitter_oauth.get_oauth1_user_handler(account))
                media = api_v1.media_upload(image_path)
                media_ids = [media.media_id]
            except (tweepy.TweepyException, socket.timeout, requests.exceptions.RequestException) as e:
                print(f"Image upload failed: {e}")
                media_ids = None
            except Exception as e:
                print(f"Image upload unexpected error: {e}")
                media_ids = None
        # Only post once, with both caption and image if available
        try:
            response = client.create_tweet(text=post.content, media_ids=media_ids)
        except (tweepy.TweepyException, socket.timeout, requests.exceptions.RequestException) as e:
            print(f"Connection error posting tweet: {e}")
            post.status = "posted"
            db_session.commit()
            return False, f"Connection error: {e}"
        except Exception as e:
            print(f"Unexpected error posting tweet: {e}")
            post.status = "posted"
            db_session.commit()
            return False, f"Unexpected error: {e}"
        print("Tweet posted successfully 🎉")
        # Save X post ID for engagement tracking
        if response and hasattr(response, 'data') and 'id' in response.data:
            post.x_post_id = str(response.data['id'])
            post.status = "posted"
            db_session.commit()
        return True, "Posted successfully."
    except (tweepy.TweepyException, socket.timeout, requests.exceptions.RequestException) as e:
        print("Tweepy or connection error:", e)
        post.status = "posted"
        db_session.commit()
        return False, f"Connection error: {e}"
    except Exception as e:
        print("Unexpected error:", e)
        post.status = "posted"
        db_session.commit()
        return False, f"Unexpected error: {e}"




def process_pending_posts():
    db_session = database.SessionLocal()
    now = datetime.now()

    # Fetch posts that are pending and ready to go
    pending_posts = db_session.query(crud.models.Post).filter(
        crud.models.Post.status == "pending",
        crud.models.Post.scheduled_time <= now
    ).all()

    for post in pending_posts:
        if post.platform == "x":
            success, msg = post_to_twitter(post, db_session)
        else:
            success, msg = False, f"Platform {post.platform} not supported yet."

        # Only update status if post_to_twitter() didn't already set it
        if not post.status or post.status == "pending":
            post.status = "posted" if success else "posted"

        # Record actual posting attempt time for tracking
        post.attempted_time = now

        db_session.commit()
        print(f"[{now}] Post ID {post.id} → {post.status.upper()} | {msg}")

    db_session.close()


if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(process_pending_posts, 'interval', seconds=60)
    scheduler.start()
    print("Post Scheduler started. Press Ctrl+C to exit.")
    try:
        while True:
            time.sleep(10)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("Scheduler stopped.")
