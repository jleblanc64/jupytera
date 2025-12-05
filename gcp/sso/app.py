import os
import json
import requests
from flask import Flask, redirect, url_for, session, request, render_template

# --- SECURITY WARNING ---
# In a real application, you must set these as environment variables or use a secret management system.
# NEVER hardcode secrets in a production environment.
CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "YOUR_GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "YOUR_GOOGLE_CLIENT_SECRET")
# The email you want to exclusively allow access to
ALLOWED_EMAIL = "dabadich@gmail.com"

# Google OAuth 2.0 Configuration
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

# Fetch dynamic endpoints from Google
def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

app = Flask(__name__)
# Generate a strong, random secret key for session management
app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24))

# --- TEMPLATE ---
# The front-end view for the main page (securely embedded below)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Google SSO App</title>
    <style>
        body { font-family: sans-serif; text-align: center; margin-top: 50px; background-color: #f4f4f9; }
        .container { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); max-width: 400px; margin: auto; }
        h1 { color: #4285F4; margin-bottom: 20px; }
        .email-display { font-size: 1.2em; font-weight: bold; color: #34a853; margin: 20px 0; padding: 10px; border: 1px solid #e0e0e0; border-radius: 6px; }
        .button { background-color: #fbbc05; color: white; padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; text-decoration: none; display: inline-block; }
        .error-message { color: #ea4335; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <!-- Content inserted here by Flask -->
        %s
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    if "email" in session:
        # User is logged in, show the main page with the email
        content = f"""
            <h1>Authentication Successful!</h1>
            <p>You are logged in as:</p>
            <div class="email-display">{session['email']}</div>
            <a href="{url_for('logout')}" class="button">Logout</a>
        """
        return HTML_TEMPLATE % content
    else:
        # User is not logged in, show the login button
        content = f"""
            <h1>Welcome to the SSO Demo</h1>
            <p>Please log in using Google to continue.</p>
            <a href="{url_for('login')}" class="button">Login with Google</a>
        """
        return HTML_TEMPLATE % content

@app.route("/login")
def login():
    # Find Google's authorization endpoint
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use the client ID, scopes, and redirect URI to generate the URL
    request_uri = requests.Request(
        "GET",
        authorization_endpoint,
        params={
            "client_id": CLIENT_ID,
            "response_type": "code",
            "scope": "openid email profile", # Request permission to get basic profile and email
            "redirect_uri": request.base_url + "/callback",
            "prompt": "select_account",
        }
    ).prepare().url

    # Redirect user to Google's login page
    return redirect(request_uri)

@app.route("/login/callback")
def callback():
    # Get authorization code from Google's response
    code = request.args.get("code")
    if not code:
        # Handle error if Google didn't return a code (e.g., user denied access)
        content = """
            <h1 class="error-message">Login Failed</h1>
            <p>Access was denied by the user or an error occurred.</p>
            <a href="/" class="button">Go Home</a>
        """
        return HTML_TEMPLATE % content, 403

    # 1. Exchange the code for a token (server-to-server)
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    token_response = requests.post(
        token_endpoint,
        data={
            "code": code,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": request.base_url, # Must match the URL used in the /login step
            "grant_type": "authorization_code",
        },
    )

    # Check for token response errors
    token_response.raise_for_status()
    tokens = token_response.json()

    # 2. Get user info (email) using the access token
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    userinfo_response = requests.get(
        userinfo_endpoint,
        headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    userinfo_response.raise_for_status()
    user_data = userinfo_response.json()

    user_email = user_data.get("email")

    # 3. --- AUTHORIZATION CHECK (The specific rule you requested) ---
    if user_email != ALLOWED_EMAIL:
        # Reject access if the verified email does not match
        content = f"""
            <h1 class="error-message">Access Denied</h1>
            <p>The email <strong>{user_email}</strong> is not authorized to access this application.</p>
            <p>Only <strong>{ALLOWED_EMAIL}</strong> is allowed.</p>
            <a href="/" class="button">Try Again</a>
        """
        return HTML_TEMPLATE % content, 403

    # 4. Success: Store the email in the session and redirect
    session["email"] = user_email
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.pop("email", None)
    return redirect(url_for("index"))

# To run the application within Docker
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)