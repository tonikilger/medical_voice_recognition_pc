from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager

from webApp.models import db, User

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_app():
    app = Flask(__name__, instance_path='/var/www/webApp/webApp/instance')

    # Configure the database URI (replace with your database URI)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////var/www/webApp/webApp/instance/database.db'  # Absolute path for production  
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'the random string'

    # Initialize extensions
    db.init_app(app)
    
    # Initialize Flask-Migrate with app and db
    migrate = Migrate(app, db)

    # Flask-Login initialisieren
    login_manager = LoginManager()
    login_manager.login_view = "login.login"
    login_manager.init_app(app)

    from webApp.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .views import views, login_blueprint

    # Register Blueprints
    app.register_blueprint(views)
    app.register_blueprint(login_blueprint)

    return app

# Create the app instance for Flask CLI
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
