from flask import Blueprint, render_template, request, redirect, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

auth_routes = Blueprint('auth', __name__)

@auth_routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        email = request.form['email']
        comment = request.form['comment']
        nationality = request.form['nationality']

        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO users (username, password, email, comment, nationality) VALUES (?, ?, ?, ?, ?)",
                (username, password, email, comment, nationality)
            )
            conn.commit()
            flash("Registration complete. Please log in.")
        except sqlite3.IntegrityError:
            flash("Username already exists.")
        return redirect('/login')

    return render_template('auth/register.html')

@auth_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        input_password = request.form['password']

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cur.fetchone()

        if user and check_password_hash(user['password'], input_password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect('/dashboard')
        else:
            flash("Invalid credentials.")
            return redirect('/login')

    return render_template('auth/login.html')

@auth_routes.route('/logout')
def logout():
    session.clear()
    flash("Logged out.")
    return redirect('/login')

@auth_routes.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db()
    cur = conn.cursor()

    if request.method == 'POST':
        email = request.form['email']
        comment = request.form['comment']
        nationality = request.form['nationality']
        password = request.form['password']

        if password:
            hashed = generate_password_hash(password)
            cur.execute("UPDATE users SET email=?, comment=?, nationality=?, password=? WHERE id=?", 
                        (email, comment, nationality, hashed, session['user_id']))
        else:
            cur.execute("UPDATE users SET email=?, comment=?, nationality=? WHERE id=?", 
                        (email, comment, nationality, session['user_id']))

        conn.commit()
        flash("Profile updated.")
        return redirect('/profile')

    cur.execute("SELECT * FROM users WHERE id=?", (session['user_id'],))
    user = cur.fetchone()
    return render_template('user/profile.html', user=user)