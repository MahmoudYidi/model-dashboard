from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user
from utils.auth import User

auth_bp = Blueprint('auth', __name__)

# Sample user data
users = {
    'admin': {
        'password': 'pbkdf2:sha256:260000$N2B9Jz5Y7b8O9P0Q$1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z'
    }
}

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in users and password == 'password':  # For testing only
            user = User(username)
            login_user(user)
            return redirect(url_for('main.home'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))