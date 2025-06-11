from flask import Flask
from flask_migrate import Migrate
from models import db
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


# Initialize SQLAlchemy

migrate = Migrate()  # Initialize Flask-Migrate

def create_app():
    app = Flask(__name__)

    # Configure the database URI (replace with your database URI)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'the random string'
    import models

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)  # Bind Flask-Migrate to the app and SQLAlchemy
    from views import views

    # Register Blueprints
    app.register_blueprint(views)
    

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
