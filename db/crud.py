
def create_post(db, user_id, platform, content, scheduled_time):
    new_post = models.Post(
        user_id=user_id,
        platform=platform,
        content=content,
        scheduled_time=scheduled_time,
        status="pending"
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post
def delete_social_account(db, account_id):
    account = db.query(models.SocialAccount).filter_by(id=account_id).first()
    if account:
        db.delete(account)
        db.commit()
def delete_scheduled_post(db, post_id):
    post = db.query(models.Post).filter_by(id = post_id).first()
    if post:
        db.delete(post)
        db.commit()
def get_user_social_accounts(db, user_id):
    return db.query(models.SocialAccount).filter(models.SocialAccount.user_id == user_id).all()

def get_user_posts(db, user_id):
    return db.query(models.Post).filter(models.Post.user_id == user_id).order_by(models.Post.scheduled_time.desc()).all()
# social_scheduler/db/crud.py
from . import models

def save_social_tokens(db, user_id, platform, token_data):
    account = db.query(models.SocialAccount).filter_by(user_id=user_id, platform=platform).first()
    
    if account:
        account.access_token = token_data.get("access_token")
        account.access_token_secret = token_data.get("access_token_secret")  # NEW
        account.refresh_token = token_data.get("refresh_token")
        account.token_expiry = token_data.get("token_expiry")
    else:
        account = models.SocialAccount(
            user_id=user_id,
            platform=platform,
            access_token=token_data.get("access_token"),
            access_token_secret=token_data.get("access_token_secret"),  # NEW
            refresh_token=token_data.get("refresh_token"),
            token_expiry=token_data.get("token_expiry")
        )
        db.add(account)
    
    db.commit()
    db.refresh(account)
    return account
