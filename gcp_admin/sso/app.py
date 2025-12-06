import os
import json
import requests
import subprocess
from flask import Flask, redirect, url_for, session, request, Response
import time

# --- SECURITY WARNING ---
CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "YOUR_GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "YOUR_GOOGLE_CLIENT_SECRET")
GCLOUD_ACCESS_TOKEN = os.environ.get("GCLOUD_ACCESS_TOKEN", "")
print(GCLOUD_ACCESS_TOKEN)

ALLOWED_EMAIL = "dabadich@gmail.com"

GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24))

def get_redirect_uri():
    url = url_for("callback", _external=True, _scheme='https')
    if "127.0.0.1" in url:
        url = "http://127.0.0.1:5000/login/callback"

    return url

# ============================================================
# SAFE CODE EDITOR TEMPLATE
# ============================================================
CODE_EDITOR_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Edit Python Code</title>
<style>
    body { background:#1e1e1e; color:white; font-family: monospace; padding:20px; }
    textarea { width:100%; height:80vh; background:#252526; color:#d4d4d4;
               border:none; padding:15px; font-size:14px; border-radius:6px; }
    .button { background:#0e639c; padding:10px 20px; color:white;
              border:none; border-radius:6px; cursor:pointer;
              text-decoration:none; font-family:sans-serif; }
    .button:hover { opacity:0.9; }
</style>
</head>
<body>
<h1>Edit app.py</h1>
<form method="POST">
<textarea name="code">__CODE_CONTENT__</textarea>
<br><br>
<button type="submit" class="button">Save</button>
<a href="/" class="button" style="background:#444;">Cancel</a>
</form>
</body>
</html>
"""

# ============================================================
# MAIN HTML TEMPLATE
# ============================================================
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
    </style>
</head>
<body>
    <div class="container">
        %s
    </div>
</body>
</html>
"""

# --- BUILD LIVE TEMPLATE ---
BUILD_LIVE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Build Output - Live</title>
<style>
body { font-family: 'Courier New', monospace; background-color: #1e1e1e; color: #d4d4d4; padding: 20px; margin: 0; }
.container { max-width: 1200px; margin: auto; background: #252526; padding: 20px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5); }
h1 { color: #4ec9b0; margin-bottom: 10px; font-size: 24px; }
#output { background: #1e1e1e; padding: 15px; border-radius: 4px; min-height: 400px; max-height: 600px; overflow-y: auto; font-size: 14px; line-height: 1.5; white-space: pre-wrap; word-wrap: break-word; }
.line { margin: 2px 0; }
.error { color: #f48771; }
.success { color: #4ec9b0; }
.info { color: #569cd6; }
#status { margin: 15px 0; padding: 10px; border-radius: 4px; font-weight: bold; }
.running { background: #264f78; color: #4fc3f7; }
.completed { background: #0e5a0e; color: #4ec9b0; }
.failed { background: #5a1414; color: #f48771; }
.button { background-color: #0e639c; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; margin-top: 15px; font-family: sans-serif; }
.button:hover { background-color: #1177bb; }
#spinner { display: inline-block; margin-left: 10px; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.spinner-icon { border: 3px solid #3a3a3a; border-top: 3px solid #4fc3f7; border-radius: 50%; width: 16px; height: 16px; animation: spin 1s linear infinite; display: inline-block; vertical-align: middle; }
</style>
</head>
<body>
<div class="container">
<h1>🔨 Build Script Output</h1>
<div id="status" class="running">
Status: Running
<span id="spinner"><span class="spinner-icon"></span></span>
</div>
<div id="output"></div>
<a href="/" class="button">Go Back Home</a>
</div>

<script>
const outputDiv = document.getElementById('output');
const statusDiv = document.getElementById('status');
const spinner = document.getElementById('spinner');
const eventSource = new EventSource('/build/stream');

eventSource.onmessage = function(event) {
    const data = JSON.parse(event.data);
    if (data.type === 'output') {
        const line = document.createElement('div');
        line.className = 'line';
        line.textContent = data.content;
        outputDiv.appendChild(line);
        outputDiv.scrollTop = outputDiv.scrollHeight;
    } else if (data.type === 'error') {
        const line = document.createElement('div');
        line.className = 'line error';
        line.textContent = data.content;
        outputDiv.appendChild(line);
        outputDiv.scrollTop = outputDiv.scrollHeight;
    } else if (data.type === 'complete') {
        spinner.style.display = 'none';
        if (data.success) {
            statusDiv.className = 'completed';
            statusDiv.innerHTML = '✅ Status: Completed Successfully';
        } else {
            statusDiv.className = 'failed';
            statusDiv.innerHTML = `❌ Status: Failed (Exit Code: ${data.exit_code})`;
        }
        eventSource.close();
    }
};

eventSource.onerror = function(event) {
    spinner.style.display = 'none';
    statusDiv.className = 'failed';
    statusDiv.textContent = '❌ Status: Connection Error';
    eventSource.close();
};
</script>
</body>
</html>
"""


@app.route("/")
def index():
    if "email" in session:
        content = f"""
            <h1>Authentication Successful!</h1>
            <p>You are logged in as:</p>
            <div class="email-display">{session['email']}</div>
            <a href="{url_for('list_projects')}" class="button" style="background-color: #34a853;">List GCloud Projects</a>
            <a href="{url_for('run_build')}" class="button" style="background-color: #ff9800; margin-left:10px;">Run Build Script</a>
            <a href="/edit" class="button" style="background-color: #4285F4; margin-left:10px;">Edit App Code</a>
            <a href="{url_for('logout')}" class="button" style="margin-left:10px; background-color: #ea4335;">Logout</a>
        """
        return HTML_TEMPLATE % content

    content = f"""
        <h1>Welcome to the SSO Demo</h1>
        <p>Please log in using Google to continue.</p>
        <a href="{url_for('login')}" class="button">Login with Google</a>
    """
    return HTML_TEMPLATE % content

# ============================================================
# CODE EDITOR ROUTE
# ============================================================
@app.route("/edit", methods=["GET", "POST"])
def edit_code():
    if "email" not in session:
        return redirect(url_for("index"))

    target_file = "/app/voila/python/app.py"

    if request.method == "POST":
        new_code = request.form.get("code", "")
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(new_code)
        return HTML_TEMPLATE % "<h1>Code Updated</h1><p>Your changes were saved.</p><a href='/' class='button'>Return Home</a>"

    with open(target_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Safe HTML escaping
    safe_content = (
        content.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

    return CODE_EDITOR_TEMPLATE.replace("__CODE_CONTENT__", safe_content)

# ============================================================
# (Your other routes remain unchanged below)
# ============================================================

# --- BUILD PAGE ---
@app.route("/build")
def run_build():
    if "email" not in session:
        return redirect(url_for("index"))
    return BUILD_LIVE_TEMPLATE

# --- STREAM BUILD ---
@app.route("/build/stream")
def stream_build():
    if "email" not in session:
        return "Unauthorized", 401
    def generate():
        gcloud_token = os.environ.get("GCLOUD_ACCESS_TOKEN", "")
        command = ["bash", "script_build.sh"]

        custom_env = os.environ.copy()
        if gcloud_token:
            custom_env["CLOUDSDK_AUTH_ACCESS_TOKEN"] = gcloud_token

        try:
            process = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, bufsize=1, env=custom_env
            )
            for line in iter(process.stdout.readline, ''):
                yield f"data: {json.dumps({'type': 'output', 'content': line.rstrip()})}\n\n"
            for line in iter(process.stderr.readline, ''):
                yield f"data: {json.dumps({'type': 'error', 'content': line.rstrip()})}\n\n"
            process.wait()
            success = process.returncode == 0
            yield f"data: {json.dumps({'type': 'complete', 'success': success, 'exit_code': process.returncode})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
            yield f"data: {json.dumps({'type': 'complete', 'success': False, 'exit_code': -1})}\n\n"

    return Response(generate(), mimetype='text/event-stream')

# --- PROJECT LIST ---
@app.route("/projects")
def list_projects():
    if "email" not in session:
        return redirect(url_for("index"))
    if GCLOUD_ACCESS_TOKEN == "YOUR_HARDCODED_GCLOUD_TOKEN_HERE":
        content = f"""
            <h1 class="error-message">Configuration Error</h1>
            <p>The GCLOUD_ACCESS_TOKEN placeholder must be replaced.</p>
            <a href="/" class="button">Go Back</a>
        """
        return HTML_TEMPLATE % content

    PROJECTS_API_URL = "https://cloudresourcemanager.googleapis.com/v1/projects"
    headers = {"Authorization": f"Bearer {GCLOUD_ACCESS_TOKEN}"}

    try:
        response = requests.get(PROJECTS_API_URL, headers=headers)
        response.raise_for_status()
        projects = response.json().get("projects", [])
        if projects:
            html = "<ul>" + "".join(
                f"<li><strong>{p.get('name')}</strong> (ID: {p.get('projectId')})</li>"
                for p in projects
            ) + "</ul>"
            content = f"<h1>Projects</h1>{html}<a href='/' class='button'>Go Back</a>"
        else:
            content = "<h1>No Projects Found</h1><a href='/' class='button'>Go Back</a>"
    except Exception as e:
        content = f"<h1>Error</h1><p>{str(e)}</p><a href='/' class='button'>Go Back</a>"

    return HTML_TEMPLATE % content

# LOGIN + CALLBACK + LOGOUT
@app.route("/login")
def login():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    redirect_uri = get_redirect_uri()
    request_uri = requests.Request(
        "GET", authorization_endpoint,
        params={
            "client_id": CLIENT_ID,
            "response_type": "code",
            "scope": "openid email profile",
            "redirect_uri": redirect_uri,
            "prompt": "select_account",
        },
    ).prepare().url
    return redirect(request_uri)

@app.route("/login/callback")
def callback():
    code = request.args.get("code")
    redirect_uri = get_redirect_uri()
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    token_response = requests.post(
        token_endpoint,
        data={
            "code": code,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        },
    )
    token_response.raise_for_status()
    tokens = token_response.json()

    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    userinfo_response = requests.get(
        userinfo_endpoint,
        headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    userinfo_response.raise_for_status()
    user_email = userinfo_response.json().get("email")

    if user_email != ALLOWED_EMAIL:
        return HTML_TEMPLATE % f"<h1>Access Denied</h1>", 403

    session["email"] = user_email
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.pop("email", None)
    return redirect(url_for("index"))

# RUN
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
