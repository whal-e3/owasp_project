from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DB = 'database.db'

# Utility: DB connection
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

# Utility: Admin check
def is_admin():
    return session.get('username') == 'admin'

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/dashboard')
    return redirect('/login')

@app.route('/profile', methods=['GET', 'POST'])
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
    return render_template('profile.html', user=user)

@app.route('/register', methods=['GET', 'POST'])
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

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
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

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out.")
    return redirect('/login')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM challenges")
    challenges = cur.fetchall()
    return render_template('dashboard.html', challenges=challenges)

@app.route('/notices')
def notices():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM notices ORDER BY date DESC")
    notices = cur.fetchall()
    return render_template('notice.html', notices=notices)

@app.route('/leaderboard')
@app.route('/leaderboard')
def leaderboard():
    conn = get_db()
    cur = conn.cursor()

    # Get users ordered by score DESC, solved time ASC
    cur.execute("""
        SELECT u.id, u.username, u.score, u.nationality, MAX(s.solved_at) AS last_solved_time
        FROM users u
        LEFT JOIN solves s ON u.id = s.user_id
        GROUP BY u.id
        ORDER BY u.score DESC, last_solved_time ASC
        LIMIT 100
    """)
    top_users = cur.fetchall()

    # Update rankings in DB
    for i, user in enumerate(top_users, start=1):
        cur.execute("UPDATE users SET ranking=? WHERE id=?", (i, user["id"]))
    conn.commit()

    return render_template("leaderboard.html", top_users=top_users)

# ------------------ ADMIN ------------------

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if not is_admin():
        flash("Access denied.")
        return redirect('/login')

    return render_template('admin.html')

@app.route('/admin/users')
def admin_users():
    if not is_admin():
        flash("Access denied.")
        return redirect('/login')

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, username FROM users WHERE username != 'admin'")
    users = cur.fetchall()
    return render_template('admin_users.html', users=users)

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if not is_admin():
        flash("Access denied.")
        return redirect('/login')

    conn = get_db()
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    flash("User has been removed.")
    return redirect('/admin/users')

@app.route('/admin/add_challenge', methods=['POST'])
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

@app.route('/admin/add_notice', methods=['POST'])
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

# ---------

@app.route('/challenge/<int:challenge_id>', methods=['GET', 'POST'])
def challenge(challenge_id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db()
    cur = conn.cursor()

    # get challenge info
    cur.execute("SELECT * FROM challenges WHERE id=?", (challenge_id,))
    challenge = cur.fetchone()
    if not challenge:
        flash("Challenge not found.")
        return redirect('/dashboard')

    # check if already solved
    cur.execute("SELECT 1 FROM solves WHERE user_id=? AND challenge_id=?", (session['user_id'], challenge_id))
    already_solved = cur.fetchone()

    # get top 5 solvers
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
            # mark as solved
            cur.execute("INSERT INTO solves (user_id, challenge_id) VALUES (?, ?)", (session['user_id'], challenge_id))
            # update score
            cur.execute("UPDATE users SET score = score + ? WHERE id = ?", (challenge['score'], session['user_id']))
            conn.commit()
            flash("🎉 Correct flag! Challenge solved.")
            return redirect('/dashboard')
        else:
            flash("❌ Incorrect flag.")

    return render_template('challenge.html', challenge=challenge, already_solved=bool(already_solved), solvers=solvers)

if __name__ == '__main__':
    app.run(debug=True)