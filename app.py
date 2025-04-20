from flask import Flask
from routes.main import main_routes
from routes.auth import auth_routes
from routes.admin import admin_routes
from routes.challenge import challenge_routes
from routes.forum import forum_routes

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.register_blueprint(main_routes)
app.register_blueprint(auth_routes)
app.register_blueprint(admin_routes)
app.register_blueprint(challenge_routes)
app.register_blueprint(forum_routes)

if __name__ == '__main__':
    app.run(debug=True)