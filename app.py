from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this in production

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['flask_login_app']
users_collection = db['users']
audit_collection = db['audit_logs']

# Audit logging function
def log_audit(action, username, details=None):
    audit_entry = {
        'timestamp': datetime.utcnow(),
        'action': action,
        'username': username,
        'details': details,
        'ip_address': request.remote_addr
    }
    audit_collection.insert_one(audit_entry)

@app.route('/')
def index():
    if 'username' in session:
        user = users_collection.find_one({'username': session['username']})
        if user and user.get('is_admin', False):
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = users_collection.find_one({'username': username})

        if user and check_password_hash(user['password'], password):
            session['username'] = username
            log_audit('LOGIN', username)
            if user.get('is_admin', False):
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        phone = request.form.get('phone')

        # Check if user already exists
        if users_collection.find_one({'username': username}):
            return render_template('register.html', error='Username already exists')

        # Hash password and save user
        hashed_password = generate_password_hash(password)
        user_data = {
            'username': username,
            'password': hashed_password,
            'name': name,
            'phone': phone,
            'is_admin': False,
            'created_at': datetime.utcnow()
        }
        users_collection.insert_one(user_data)
        log_audit('USER_CREATED', username, f'User {username} registered')

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    user = users_collection.find_one({'username': username})
    if user and user.get('is_admin', False):
        return redirect(url_for('admin_dashboard'))

    return render_template('home.html', user=user)

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    user = users_collection.find_one({'username': session['username']})
    if not user or not user.get('is_admin', False):
        return redirect(url_for('login'))

    # Get all users
    users = list(users_collection.find({}, {'password': 0}))

    # Get recent audit logs
    audit_logs = list(audit_collection.find().sort('timestamp', -1).limit(50))

    return render_template('admin_dashboard.html', user=user, users=users, audit_logs=audit_logs)

@app.route('/admin/create_user', methods=['POST'])
def admin_create_user():
    if 'username' not in session:
        return redirect(url_for('admin_login'))

    user = users_collection.find_one({'username': session['username']})
    if not user or not user.get('is_admin', False):
        return redirect(url_for('login'))

    username = request.form.get('username')
    password = request.form.get('password')
    name = request.form.get('name')
    phone = request.form.get('phone')

    if users_collection.find_one({'username': username}):
        return redirect(url_for('admin_dashboard'))

    hashed_password = generate_password_hash(password)
    user_data = {
        'username': username,
        'password': hashed_password,
        'name': name,
        'phone': phone,
        'is_admin': False,
        'created_at': datetime.utcnow()
    }
    users_collection.insert_one(user_data)
    log_audit('ADMIN_USER_CREATED', session['username'], f'Created user: {username}')

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_user/<username>')
def admin_delete_user(username):
    if 'username' not in session:
        return redirect(url_for('admin_login'))

    user = users_collection.find_one({'username': session['username']})
    if not user or not user.get('is_admin', False):
        return redirect(url_for('login'))

    if username != 'admin':  # Prevent deleting admin
        users_collection.delete_one({'username': username})
        log_audit('ADMIN_USER_DELETED', session['username'], f'Deleted user: {username}')

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/change_password/<username>', methods=['POST'])
def admin_change_password(username):
    if 'username' not in session:
        return redirect(url_for('admin_login'))

    user = users_collection.find_one({'username': session['username']})
    if not user or not user.get('is_admin', False):
        return redirect(url_for('login'))

    new_password = request.form.get('new_password')
    if new_password:
        hashed_password = generate_password_hash(new_password)
        users_collection.update_one(
            {'username': username},
            {'$set': {'password': hashed_password}}
        )
        log_audit('ADMIN_PASSWORD_CHANGED', session['username'], f'Changed password for: {username}')

    return redirect(url_for('admin_dashboard'))

@app.route('/logout')
def logout():
    if 'username' in session:
        log_audit('LOGOUT', session['username'])
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)