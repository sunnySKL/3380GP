import os
import requests
from flask import Blueprint, redirect, url_for, session, flash, request

auth = Blueprint('auth', __name__)

# Load secrets 
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")
#REDIRECT_URI = os.getenv("REDIRECT_URI")
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/authorize"
TOKEN_URL = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
SCOPE = ["User.Read"]

@auth.route("/login")
def microsoft_login():
    if "user" in session:
        print("[DEBUG] User already in session, redirecting to dashboard...")
        return redirect(url_for("admin.dashboard"))  # Prevents re-login loop

    #print("[DEBUG] Redirecting user to Microsoft login...")
    redirect_uri = url_for('auth.microsoft_callback', _external=True)
    print(f"Generated redirect uri: {redirect_uri}")
    login_url = (
        f"{AUTHORITY}?client_id={CLIENT_ID}"
        f"&response_type=code&redirect_uri={redirect_uri}"
        f"&scope={' '.join(SCOPE)}"
    )
    return redirect(login_url)


@auth.route('/auth/callback')
def microsoft_callback():
    # Get the authorization code from Microsoft response
    code = request.args.get("code")
    if not code:
        flash("Login failed. No authorization code received.", "error")
        return redirect(url_for('main.home'))

    redirect_uri = url_for('auth.microsoft_callback', _external=True)

    # Exchange code for access token
    token_data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "scope": " ".join(SCOPE),
    }
    response = requests.post(TOKEN_URL, data=token_data)
    token_json = response.json()

    if "access_token" not in token_json:
        flash("Failed to authenticate with Microsoft.", "error")
        return redirect(url_for('main.home'))

    # Store token & user session
    access_token = token_json["access_token"]
    session["access_token"] = access_token

    # Get user info
    user_info = requests.get("https://graph.microsoft.com/v1.0/me", headers={"Authorization": f"Bearer {access_token}"}).json()

    session["user"] = user_info.get("displayName", "Unknown User")
    session["email"] = user_info.get("mail", "No Email Provided")

    curr_admins = ["hkliu@cougarnet.uh.edu", "eesenvar@cougarnet.uh.edu"] 
    #  Assign admin role if email matches yours
    flash(f"Welcome, {session['user']}!", "success")
    if session["email"].lower() in curr_admins:
        session["role"] = "Admin"
    else:
        session["role"] = "User"

    #flash(f"Welcome, {session['user']}!", "success")
    return redirect(url_for('admin.dashboard'))

@auth.route('/logout')
def logout():
    session.clear()
    ms_logout_url = "https://login.microsoftonline.com/common/oauth2/logout?post_logout_redirect_uri=" + url_for('main.home', _external=True)
    redirect
    print("[DEBUG] User session cleared")
    flash("You have been logged out.", "success")
    return redirect(ms_logout_url)
