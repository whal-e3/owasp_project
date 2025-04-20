# routes/main.py
from flask import Blueprint, render_template, session, redirect, flash
import sqlite3

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

main_routes = Blueprint('main', __name__)

@main_routes.route('/')
def index():
    if 'user_id' in session:
        return redirect('/dashboard')
    return redirect('/login')

@main_routes.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM challenges")
    challenges = cur.fetchall()
    cur.execute("SELECT challenge_id FROM solves WHERE user_id = ?", (session['user_id'],))
    solved_ids = {row['challenge_id'] for row in cur.fetchall()}
    return render_template('dashboard.html', challenges=challenges, solved_ids=solved_ids)

@main_routes.route('/notices')
def notices():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM notices ORDER BY date DESC")
    notices = cur.fetchall()
    return render_template('notice.html', notices=notices)

@main_routes.route('/leaderboard')
def leaderboard():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT u.id, u.username, u.nationality,
               SUM(c.score) AS total_score,
               MAX(s.solved_at) AS last_solved_time
        FROM users u
        LEFT JOIN solves s ON u.id = s.user_id
        LEFT JOIN challenges c ON s.challenge_id = c.id
        WHERE u.username != 'admin'
        GROUP BY u.id
        ORDER BY total_score DESC, last_solved_time ASC
        LIMIT 100
    """)
    top_users = cur.fetchall()
    for i, user in enumerate(top_users, start=1):
        cur.execute("UPDATE users SET ranking=? WHERE id=?", (i, user["id"]))
    conn.commit()
    return render_template("leaderboard.html", top_users=top_users)