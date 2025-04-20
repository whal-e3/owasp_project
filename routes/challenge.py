# routes/challenge.py
from flask import Blueprint, render_template, request, session, redirect, flash
import sqlite3

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

challenge_routes = Blueprint('challenge', __name__)

@challenge_routes.route('/challenge/<int:challenge_id>', methods=['GET', 'POST'])
def challenge(challenge_id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db()
    cur = conn.cursor()

    # Get challenge info
    cur.execute("SELECT * FROM challenges WHERE id=?", (challenge_id,))
    challenge = cur.fetchone()
    if not challenge:
        flash("Challenge not found.")
        return redirect('/dashboard')

    # Check if already solved
    cur.execute("SELECT 1 FROM solves WHERE user_id=? AND challenge_id=?", (session['user_id'], challenge_id))
    already_solved = cur.fetchone()

    # Get top 5 solvers
    cur.execute("""
        SELECT u.username, s.solved_at
        FROM solves s JOIN users u ON s.user_id = u.id
        WHERE s.challenge_id = ?
        ORDER BY s.solved_at ASC
        LIMIT 5
    """, (challenge_id,))
    solvers = cur.fetchall()

    if request.method == 'POST':
        submitted_flag = request.form['flag'].strip()
        if already_solved:
            flash("You've already solved this challenge.")
            return redirect(f'/challenge/{challenge_id}')
        if submitted_flag == challenge['flag']:
            cur.execute("INSERT INTO solves (user_id, challenge_id) VALUES (?, ?)", (session['user_id'], challenge_id))
            cur.execute("UPDATE users SET score = score + ? WHERE id = ?", (challenge['score'], session['user_id']))
            conn.commit()
            flash("🎉 Correct flag! Challenge solved.")
            return redirect('/dashboard')
        else:
            flash("❌ Incorrect flag.")

    return render_template('challenge/challenge.html', challenge=challenge, already_solved=bool(already_solved), solvers=solvers)