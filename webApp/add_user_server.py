#!/usr/bin/env python3
"""
Script to add a user on the server via Flask CLI
"""
import sys
import os

# Add the webApp directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'the random string'

# Initialize database
db = SQLAlchemy()
db.init_app(app)

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_username(self, username):
        self.username = username

def add_user_server():
    with app.app_context():
        # Check if doctor user already exists
        existing_user = User.query.filter_by(username='doctor').first()
        if existing_user:
            # Update existing user's password
            existing_user.set_password('1369')
            existing_user.is_admin = False
            db.session.commit()
            print("User 'doctor' already exists - password updated!")
            print("Username: doctor")
            print("Password: 1369")
            print("Admin rights: No")
            return
        
        # Create new doctor user
        new_user = User()
        new_user.set_username('doctor')
        new_user.set_password('1369')
        new_user.is_admin = False
        
        db.session.add(new_user)
        db.session.commit()
        
        print("User 'doctor' successfully created!")
        print("Username: doctor")
        print("Password: 1369")
        print("Admin rights: No")

if __name__ == '__main__':
    add_user_server()
