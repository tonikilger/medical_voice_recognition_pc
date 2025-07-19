#!/usr/bin/env python3
"""
Script to add a new user to the Medical Voice Recorder application
"""
import os
import sys
from webApp import app
from webApp.models import db, User

def add_user(username, password, is_admin=False):
    """Add a new user to the database"""
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"User '{username}' already exists!")
            return False
        
        # Create new user
        new_user = User()
        new_user.set_username(username)
        new_user.set_password(password)
        new_user.is_admin = is_admin
        
        try:
            db.session.add(new_user)
            db.session.commit()
            print(f"User '{username}' successfully added!")
            print(f"Admin privileges: {is_admin}")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error adding user: {e}")
            return False

def list_users():
    """List all existing users"""
    with app.app_context():
        users = User.query.all()
        print("\nExisting users:")
        print("-" * 40)
        for user in users:
            admin_status = "Admin" if user.is_admin else "Regular User"
            print(f"Username: {user.username} | Status: {admin_status}")
        print("-" * 40)

if __name__ == '__main__':
    print("Medical Voice Recorder - User Management")
    print("=" * 50)
    
    # First, show existing users
    list_users()
    
    # Add the doctor user
    print("\nAdding new user 'doctor'...")
    
    # You can change the password here
    doctor_password = "doctor123"  # Change this to a secure password
    
    success = add_user("doctor", doctor_password, is_admin=False)
    
    if success:
        print("\n✅ User 'doctor' has been successfully added!")
        print(f"Username: doctor")
        print(f"Password: {doctor_password}")
        print("Admin privileges: No")
        
        # Show updated user list
        list_users()
    else:
        print("\n❌ Failed to add user 'doctor'")
    
    print("\nScript completed.")
