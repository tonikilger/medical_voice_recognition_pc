from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager

import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_app():
    # Use local instance path for development, production path for deployment
    import os
    if os.path.exists('/var/www/webApp/'):
        instance_path = '/var/www/webApp/webApp/instance'
    else:
        instance_path = None  # Use Flask default
        
    app = Flask(__name__, instance_path=instance_path)

    # Configure the database URI (replace with your database URI)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'the random string'

    # Import models after app config but before init_app
    from webApp.models import db, User
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize Flask-Migrate with app and db
    migrate = Migrate(app, db)

    # Flask-Login initialisieren
    login_manager = LoginManager()
    login_manager.login_view = "login.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        with app.app_context():
            return User.query.get(int(user_id))

    # Import views after all extensions are initialized
    from webApp.views import views
    from webApp.views import login_blueprint

    # Register Blueprints
    app.register_blueprint(views)
    app.register_blueprint(login_blueprint)

    # Create database tables within app context
    with app.app_context():
        db.create_all()

    return app

# Create the app instance for WSGI
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)