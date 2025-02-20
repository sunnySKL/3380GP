from flask import Blueprint, render_template, session, redirect, url_for, flash, request
import app.services.user_services as user_service
from app.models import User
from app.decorators import admin_required

admin = Blueprint("admin", __name__)

@admin.route("/admin/dashboard")
@admin_required
def dashboard():
    if "user" not in session:
        flash("Please log in to access the dashboard", "error")
        return redirect(url_for("auth.microsoft_login"))

    # Restrict access to Admins only
    #if session.get("role") != "Admin":
    #    flash("Access Denied: Admins Only!", "error")
    #    return redirect(url_for("main.home"))

    # Temporary Hardcoded Users (Replace with Database Query Later)
    #users = [
    #    {"id": 1, "name": "Alice", "email": "alice@example.com", "role": "User", "status": "Active"},
    #    {"id": 2, "name": "Bob", "email": "bob@example.com", "role": "Admin", "status": "Active"},
    #]

    users = user_service.get_all_users()

    return render_template("admin.html", user=session["user"], email=session["email"], role=session["role"], users=users)


@admin.route("/admin/update_user")
@admin_required
def update_user():
    pass

@admin.route("/admin/delete_user/<int:user_id>", methods = ["POST"])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    user_service.delete_user(user)
    flash("User deleted successfully!", "success")
    return redirect(url_for('admin.dashboard'))

@admin.route("/admin/create_user", methods = ["POST"])
@admin_required
def create_user():
    # Get data from the form submission
    display_name = request.form.get('display_name')
    email = request.form.get('email')
    role = request.form.get('role', 'User')
    status = request.form.get('status', 'active')

    # Validate required fields
    if not display_name or not email:
        flash("Name and Email are required.", "error")
        return redirect(url_for('admin.dashboard'))

    # Create a new User instance
    user_service.create_user(display_name, email, role, status)
    #new_user = User(display_name=display_name, email=email, role=role, status=status)

    flash("User created successfully!", "success")
    return redirect(url_for('admin.dashboard'))

