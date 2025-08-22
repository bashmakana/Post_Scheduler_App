import threading
import http.server
import socketserver
import urllib.parse
import webbrowser
import tweepy
import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()

from db import crud, database
from sqlalchemy.orm import Session
from datetime import datetime

def get_oauth1_user_handler(account):
    import tweepy
    return tweepy.OAuth1UserHandler(
        consumer_key=API_KEY,
        consumer_secret=API_SECRET,
        access_token=account.access_token,
        access_token_secret=account.access_token_secret
    )


API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
CALLBACK_URL = "http://localhost:8000"

OAUTH_REQUEST_TOKEN_KEY = "twitter_request_token"
OAUTH_REQUEST_TOKEN_SECRET_KEY = "twitter_request_token_secret"
OAUTH_VERIFIER_KEY = "twitter_oauth_verifier"
ACCESS_TOKEN_KEY = "twitter_access_token"
ACCESS_TOKEN_SECRET_KEY = "twitter_access_token_secret"

class OAuthHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        if "oauth_verifier" in params:
            verifier = params["oauth_verifier"][0]
            st.session_state[OAUTH_VERIFIER_KEY] = verifier
            print(f"[DEBUG] Received oauth_verifier: {verifier}")
            html = f"""
                <html>
                <head><title>Twitter OAuth Completed</title></head>
                <body>
                    <h2>Twitter OAuth completed!</h2>
                    <p>Your verifier code is:</p>
                    <pre style='font-size:1.5em; color:blue;'>{verifier}</pre>
                    <p>Copy this code and paste it into the app to complete authentication.</p>
                </body>
                </html>
            """
            self.wfile.write(html.encode())
        else:
            print("[DEBUG] No oauth_verifier found in callback params.")
            html = """
                <html>
                <head><title>Twitter OAuth Error</title></head>
                <body>
                    <h2>Error: No verifier code found.</h2>
                    <p>Please try the authentication process again.</p>
                </body>
                </html>
            """
            self.wfile.write(html.encode())
        print(f"[DEBUG] Callback handled. Params: {params}")

def run_server():
    try:
        with socketserver.TCPServer(("", 8000), OAuthHandler) as httpd:
            httpd.handle_request()
    except Exception as e:
        st.error(f"Error running HTTP server: {str(e)}")

def start_local_http_server():
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()

def get_oauth_handler():
    return tweepy.OAuth1UserHandler(
        consumer_key=API_KEY,
        consumer_secret=API_SECRET,
        callback=CALLBACK_URL,
    )

def start_auth_flow():
    auth = get_oauth_handler()
    import socket
    import requests
    try:
        redirect_url = auth.get_authorization_url()
        st.session_state[OAUTH_REQUEST_TOKEN_KEY] = auth.request_token.get("oauth_token")
        st.session_state[OAUTH_REQUEST_TOKEN_SECRET_KEY] = auth.request_token.get("oauth_token_secret")
        start_local_http_server()
        webbrowser.open(redirect_url)
        return True, redirect_url
    except (tweepy.TweepyException, socket.timeout, requests.exceptions.RequestException) as e:
        st.error(f"Connection error during Twitter OAuth: {e}")
        return False, f"Connection error: {e}"
    except Exception as e:
        st.error(f"Unexpected error during Twitter OAuth: {e}")
        return False, f"Unexpected error: {e}"


def complete_auth_flow(user_id: int, db_session: Session):
    import socket
    import requests
    try:
        auth = get_oauth_handler()
        auth.request_token = {
            "oauth_token": st.session_state.get(OAUTH_REQUEST_TOKEN_KEY),
            "oauth_token_secret": st.session_state.get(OAUTH_REQUEST_TOKEN_SECRET_KEY),
        }
        verifier = st.session_state.get(OAUTH_VERIFIER_KEY)
        access_token, access_token_secret = auth.get_access_token(verifier)

        # ✅ Save BOTH tokens to DB
        token_data = {
            "access_token": access_token,
            "access_token_secret": access_token_secret,
        }
        crud.save_social_tokens(
            db=db_session,
            user_id=user_id,
            platform="x",
            token_data=token_data,
        )

        # Save in session for immediate use
        st.session_state[ACCESS_TOKEN_KEY] = access_token
        st.session_state[ACCESS_TOKEN_SECRET_KEY] = access_token_secret
        st.session_state[OAUTH_VERIFIER_KEY] = None

        return True, (access_token, access_token_secret)
    except (tweepy.TweepyException, socket.timeout, requests.exceptions.RequestException) as e:
        st.error(f"Connection error completing Twitter OAuth: {e}")
        return False, f"Connection error: {e}"
    except Exception as e:
        st.error(f"Unexpected error completing Twitter OAuth: {e}")
        return False, f"Unexpected error: {e}"
