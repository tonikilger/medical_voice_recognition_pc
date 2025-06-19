from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from models import db, User
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # Configure the database URI (replace with your database URI)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'the random string'

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Flask-Login initialisieren
    login_manager = LoginManager()
    login_manager.login_view = "login.login"
    login_manager.init_app(app)

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    import models
    from views import views
    from views import login_blueprint

    # Register Blueprints
    app.register_blueprint(views)
    app.register_blueprint(login_blueprint)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
