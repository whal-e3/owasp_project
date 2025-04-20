# routes/forum.py
from flask import Blueprint, render_template, request, redirect, session, flash, send_from_directory
import sqlite3, os
from werkzeug.utils import secure_filename

forum_routes = Blueprint('forum', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'py', 'txt', 'zip'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@forum_routes.route('/forum')
def forum():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT posts.*, users.username, challenges.title AS challenge_title
        FROM posts
        LEFT JOIN users ON posts.user_id = users.id
        LEFT JOIN challenges ON posts.challenge_id = challenges.id
        ORDER BY posts.created_at DESC
    """)
    posts = cur.fetchall()
    return render_template('forum/forum.html', posts=posts)

@forum_routes.route('/forum/<int:post_id>', methods=['GET', 'POST'])
def view_post(post_id):
    conn = get_db()
    cur = conn.cursor()

    if request.method == 'POST':
        if 'user_id' not in session:
            return redirect('/login')
        content = request.form['comment']
        cur.execute("INSERT INTO comments (post_id, user_id, content) VALUES (?, ?, ?)",
                    (post_id, session['user_id'], content))
        conn.commit()
        flash("Comment added.")
        return redirect(f'/forum/{post_id}')

    cur.execute("SELECT p.*, u.username FROM posts p JOIN users u ON p.user_id = u.id WHERE p.id = ?", (post_id,))
    post = cur.fetchone()
    cur.execute("SELECT c.*, u.username FROM comments c JOIN users u ON c.user_id = u.id WHERE c.post_id = ? ORDER BY c.created_at ASC", (post_id,))
    comments = cur.fetchall()
    return render_template('forum/post.html', post=post, comments=comments)

@forum_routes.route('/forum/new', methods=['GET', 'POST'])
def new_post():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db()
    cur = conn.cursor()

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        challenge_id = request.form.get('challenge_id') or None
        file = request.files.get('file')
        filename = None

        if file and file.filename:
            from werkzeug.utils import secure_filename
            filename = secure_filename(file.filename)
            file.save(os.path.join('uploads', filename))

        cur.execute(
            "INSERT INTO posts (user_id, title, content, filename, challenge_id) VALUES (?, ?, ?, ?, ?)",
            (session['user_id'], title, content, filename, challenge_id)
        )
        conn.commit()
        flash("Post submitted.")
        return redirect('/forum')

    # 🟢 Load challenges here
    cur.execute("SELECT id, title FROM challenges")
    challenges = cur.fetchall()

    return render_template('forum/new_post.html', post=None, challenges=challenges)

@forum_routes.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@forum_routes.route('/forum/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db()
    cur = conn.cursor()

    # Fetch post
    cur.execute("SELECT * FROM posts WHERE id=?", (post_id,))
    post = cur.fetchone()

    # Verify ownership
    if not post or post['user_id'] != session['user_id']:
        flash("You do not have permission to edit this post.")
        return redirect('/forum')

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        challenge_id = request.form.get('challenge_id') or None

        # Update with or without new file
        file = request.files.get('file')
        filename = post['filename']  # Default to existing

        if file and file.filename:
            from werkzeug.utils import secure_filename
            import os
            ALLOWED_EXTENSIONS = {'py', 'txt', 'zip'}
            def allowed_file(filename):
                return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join('uploads', filename))

        cur.execute("UPDATE posts SET title=?, content=?, challenge_id=?, filename=? WHERE id=?",
                    (title, content, challenge_id, filename, post_id))
        conn.commit()
        flash("Post updated.")
        return redirect(f"/forum/{post_id}")

    # Load challenges for dropdown
    cur.execute("SELECT id, title FROM challenges")
    challenges = cur.fetchall()

    return render_template("forum/new_post.html", post=post, challenges=challenges)