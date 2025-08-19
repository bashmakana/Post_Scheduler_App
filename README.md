# X Post Scheduler App

A modern Streamlit web app to schedule posts to X (Twitter), manage accounts, and track engagement metrics. Features include:

- Secure login/signup with tabbed UI
- Connect/disconnect X accounts via OAuth
- Schedule posts with images/media
- View scheduled and posted tweets
- Track engagement metrics (likes, retweets, replies)
- Modern, responsive UI

## Setup

1. Clone the repo
2. Install dependencies: `pip install -r requirements.txt`
3. Run the app: `streamlit run app.py`

## Configuration
- Add your X API credentials to `.env` or `X.env`
- The app uses SQLite by default (`social_scheduler.db`)

## Folder Structure
- `app.py` - Main entry point
- `ui/` - Streamlit UI components
- `db/` - Database models and CRUD
- `auth/` - Auth logic
- `oauth_clients/` - Twitter OAuth logic
- `scheduler/` - Post scheduling logic
