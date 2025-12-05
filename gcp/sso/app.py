import os
import json
import requests
# Import subprocess to run the shell script
import subprocess
from flask import Flask, redirect, url_for, session, request, render_template

# --- SECURITY WARNING ---
# In a real application, you must set these as environment variables or use a secret management system.
# NEVER hardcode secrets in a production environment.
CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "YOUR_GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "YOUR_GOOGLE_CLIENT_SECRET")
GCLOUD_ACCESS_TOKEN = os.environ.get("GCLOUD_ACCESS_TOKEN", "")
print(GCLOUD_ACCESS_TOKEN)

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
        .container { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); max-width: 600px; margin: auto; }
        h1 { color: #4285F4; margin-bottom: 20px; }
        .email-display { font-size: 1.2em; font-weight: bold; color: #34a853; margin: 20px 0; padding: 10px; border: 1px solid #e0e0e0; border-radius: 6px; }
        .button { background-color: #fbbc05; color: white; padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; text-decoration: none; display: inline-block; transition: background-color 0.3s; }
        .button:hover { opacity: 0.9; }
        .error-message { color: #ea4335; font-weight: bold; }
        ul { list-style: none; padding: 0; text-align: left; max-height: 300px; overflow-y: auto; border: 1px solid #e0e0e0; padding: 10px; border-radius: 6px; }
        li { background: #f9f9f9; margin-bottom: 8px; padding: 10px; border-radius: 4px; border-left: 5px solid #4285F4; }
    </style>
</head>
<body>
    <div class="container">
        %s
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    if "email" in session:
        # User is logged in, show the main page with the email and the new buttons
        content = f"""
            <h1>Authentication Successful!</h1>
            <p>You are logged in as:</p>
            <div class="email-display">{session['email']}</div>
            <a href="{url_for('list_projects')}" class="button" style="margin-top: 15px; background-color: #34a853;">List GCloud Projects</a>
            <a href="{url_for('run_build')}" class="button" style="margin-top: 15px; background-color: #ff9800; margin-left: 10px;">Run Build Script</a>
            <a href="{url_for('logout')}" class="button" style="margin-top: 15px; margin-left: 10px; background-color: #ea4335;">Logout</a>
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

# --- NEW ROUTE TO RUN BUILD SCRIPT ---
@app.route("/build")
def run_build():
    if "email" not in session:
        return redirect(url_for("index"))

    gcloud_token = os.environ.get("GCLOUD_ACCESS_TOKEN", "")
    command = ["bash", "script_build.sh"]

    custom_env = os.environ.copy()
    if gcloud_token:
        # This is the variable gcloud CLI checks for a pre-supplied token.
        custom_env["CLOUDSDK_AUTH_ACCESS_TOKEN"] = gcloud_token

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,  # Don't raise exception on non-zero exit code
            timeout=30,
            env=custom_env
        )

        # Combine stdout and stderr to capture all output
        output_lines = result.stdout.splitlines()
        error_lines = result.stderr.splitlines()

        # Build HTML with both stdout and stderr
        all_lines = output_lines + error_lines
        output_html = "<ul>" + "".join(f"<li>{line}</li>" for line in all_lines) + "</ul>"

        # Or if you want to distinguish between normal output and errors:
        output_html = ""
        if output_lines:
            output_html += "<strong>Output:</strong><ul>" + "".join(f"<li>{line}</li>" for line in output_lines) + "</ul>"
        if error_lines:
            output_html += "<strong>Errors:</strong><ul style='color: red;'>" + "".join(f"<li>{line}</li>" for line in error_lines) + "</ul>"

        content = f"""
            <h1>✅ Build Script Succeeded</h1>
            <p>The **script_build.sh** script ran successfully at {os.getcwd()}.</p>
            <h2>Script Output:</h2>
            {output_html}
            <a href="{url_for('index')}" class="button" style="margin-top: 20px; background-color: #4285F4;">Go Back Home</a>
        """
    except subprocess.CalledProcessError as e:
        # Build failed message
        output_lines = (e.stdout + "\n" + e.stderr).strip().splitlines()
        output_html = "<ul>" + "".join(f"<li>{line}</li>" for line in output_lines) + "</ul>"

        content = f"""
            <h1 class="error-message">❌ Build Script Failed</h1>
            <p>The **script_build.sh** script returned an error (Exit Code: {e.returncode}).</p>
            <h2>Error Output:</h2>
            {output_html}
            <a href="{url_for('index')}" class="button" style="margin-top: 20px; background-color: #4285F4;">Go Back Home</a>
        """
    except Exception as e:
        content = f"""
            <h1 class="error-message">Error</h1>
            <p>An unexpected error occurred while trying to run the script: {str(e)}</p>
            <a href="{url_for('index')}" class="button" style="margin-top: 20px; background-color: #4285F4;">Go Back Home</a>
        """

    return HTML_TEMPLATE % content
# -------------------------------------


@app.route("/projects")
def list_projects():
    if "email" not in session:
        return redirect(url_for("index"))

    # Check if a token is provided (it must be replaced for functionality)
    if GCLOUD_ACCESS_TOKEN == "YOUR_HARDCODED_GCLOUD_TOKEN_HERE":
        content = f"""
            <h1 class="error-message">Configuration Error</h1>
            <p>The GCLOUD_ACCESS_TOKEN placeholder must be replaced with a valid Google Cloud Access Token to fetch projects.</p>
            <p>The application is otherwise functional.</p>
            <a href="{url_for('index')}" class="button" style="margin-top: 20px; background-color: #4285F4;">Go Back</a>
        """
        return HTML_TEMPLATE % content

    # API Configuration
    PROJECTS_API_URL = "https://cloudresourcemanager.googleapis.com/v1/projects"

    # 1. Make the API request with the hardcoded token
    headers = {
        "Authorization": f"Bearer {GCLOUD_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(PROJECTS_API_URL, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        projects_data = response.json()
        projects = projects_data.get("projects", [])

        if projects:
            # Format results for display
            project_list_html = "<ul>"
            for p in projects:
                name = p.get('name', 'N/A')
                id = p.get('projectId', 'N/A')
                state = p.get('lifecycleState', 'N/A')
                project_list_html += f"<li><strong>{name}</strong> (ID: {id}) - Status: {state}</li>"
            project_list_html += "</ul>"

            content = f"""
                <h1>GCloud Projects Found: {len(projects)}</h1>
                <p>Retrieved projects using the hardcoded token:</p>
                {project_list_html}
                <a href="{url_for('index')}" class="button" style="margin-top: 20px; background-color: #4285F4;">Go Back</a>
            """
        else:
            content = """
                <h1>GCloud Projects</h1>
                <p>No projects found or the API returned an empty list.</p>
                <a href="{url_for('index')}" class="button" style="margin-top: 20px; background-color: #4285F4;">Go Back</a>
            """

    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP {e.response.status_code}: {e.response.reason}"
        content = f"""
            <h1 class="error-message">GCloud API Failed</h1>
            <p>Could not retrieve projects. The hardcoded token {GCLOUD_ACCESS_TOKEN} is likely invalid, expired, or unauthorized.</p>
            <p class="error-message">Details: {error_msg}</p>
            <a href="{url_for('index')}" class="button" style="margin-top: 20px; background-color: #4285F4;">Go Back</a>
        """
    except Exception as e:
        content = f"""
            <h1 class="error-message">Error</h1>
            <p>An unexpected error occurred: {str(e)}</p>
            <a href="{url_for('index')}" class="button" style="margin-top: 20px; background-color: #4285F4;">Go Back</a>
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