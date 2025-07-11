from test import app
from flask_migrate import upgrade
import os

# Set Flask app context
with app.app_context():
    # Check if migrations directory exists
    if not os.path.exists('migrations'):
        print("Migrations directory not found. Creating initial migration...")
        from flask_migrate import init, migrate
        init()
        migrate(message='Initial migration with is_admin field')
        print("Initial migration created.")
    
    # Run upgrade
    try:
        upgrade()
        print("✓ Database migration completed successfully!")
    except Exception as e:
        print(f"Migration error: {e}")
        
    # Check if admin user exists and set admin status
    from models import User, db
    users = User.query.all()
    if users:
        admin_user = users[0]  # First user becomes admin
        admin_user.is_admin = True
        db.session.commit()
        print(f"✓ User '{admin_user.username}' set as admin")
    else:
        print("No users found in database")
        
    print("\nCurrent users:")
    for user in User.query.all():
        status = "Admin" if user.is_admin else "Normal"
        print(f"  - {user.username}: {status}")
