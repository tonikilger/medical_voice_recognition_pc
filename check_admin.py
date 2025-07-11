from flask import Flask
from models import db, User
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'

db.init_app(app)

with app.app_context():
    # Check existing users
    users = User.query.all()
    print("Existing users:")
    for user in users:
        print(f"  - {user.username} (admin: {user.is_admin})")
    
    # Create admin user if none exists
    admin_users = User.query.filter_by(is_admin=True).all()
    if not admin_users:
        print("\nNo admin users found. Creating default admin user...")
        admin_user = User(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Created admin user: username='admin', password='admin123'")
        print("Please change the password after first login!")
    else:
        print(f"\nAdmin users found: {len(admin_users)}")
