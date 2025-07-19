from flask import Flask
from flask_migrate import Migrate
from models import db
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Initialize Flask-Migrate
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    # Configure the database URI (replace with your database URI)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'the random string'
    
    # Import models to ensure they are registered
    import models

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)  # Bind Flask-Migrate to the app and SQLAlchemy
    
    # Import and register views
    from views import views
    app.register_blueprint(views)
    
    # Create database tables within app context
    with app.app_context():
        db.create_all()

    return app

# Create the application instance for WSGI deployment
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)