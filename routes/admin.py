from flask import Blueprint, render_template, request, redirect, session, flash
import sqlite3

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def is_admin():
    return session.get('username') == 'admin'

admin_routes = Blueprint('admin', __name__)

@admin_routes.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if not is_admin():
        flash("Access denied.")
        return redirect('/login')
    return render_template('admin.html')

@admin_routes.route('/admin/users')
def admin_users():
    if not is_admin():
        flash("Access denied.")
        return redirect('/login')

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, username FROM users WHERE username != 'admin'")
    users = cur.fetchall()
    return render_template('admin_users.html', users=users)

@admin_routes.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if not is_admin():
        flash("Access denied.")
        return redirect('/login')

    conn = get_db()
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    flash("User has been removed.")
    return redirect('/admin/users')

@admin_routes.route('/admin/add_challenge', methods=['POST'])
def add_challenge():
    if not is_admin():
        return redirect('/')

    title = request.form['title']
    difficulty = request.form['difficulty']
    score = request.form['score']

    conn = get_db()
    conn.execute("INSERT INTO challenges (title, difficulty, score) VALUES (?, ?, ?)", (title, difficulty, score))
    conn.commit()
    flash("Challenge added.")
    return redirect('/admin')

@admin_routes.route('/admin/add_notice', methods=['POST'])
def add_notice():
    if not is_admin():
        return redirect('/')

    title = request.form['title']
    content = request.form['content']

    conn = get_db()
    conn.execute("INSERT INTO notices (title, content) VALUES (?, ?)", (title, content))
    conn.commit()
    flash("Notice posted.")
    return redirect('/admin')