#!/usr/bin/env python3
"""Test editing discharge record to see field behavior"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_discharge_edit():
    # Import here to avoid circular imports
    from models import Recording, Patient, db
    from flask import Flask
    
    # Create Flask app with proper config
    app = Flask(__name__)
    # Use absolute path to database file
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'database.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        print("=== TESTING DISCHARGE EDIT BEHAVIOR ===")
        
        # Find the discharge record for patient 001
        discharge_record = Recording.query.filter_by(
            patient_id=1,
            recording_type='discharge'
        ).first()
        
        if not discharge_record:
            print("❌ No discharge record found!")
            return
            
        print(f"✅ Found discharge record (ID: {discharge_record.id})")
        print(f"Before edit - current_weight: {discharge_record.current_weight}")
        print(f"Before edit - estimated_dryweight: {discharge_record.estimated_dryweight}")
        print(f"Before edit - discharge_medication: {discharge_record.discharge_medication}")
        
        # Simulate adding discharge_medication
        print("\n=== SIMULATING EDIT: Adding discharge_medication ===")
        discharge_record.discharge_medication = "Test medication"
        
        # Simulate adding discharge_date
        from datetime import date
        discharge_record.discharge_date = date(2025, 7, 15)
        
        # Simulate adding lab values
        discharge_record.ntprobnp = 150.5
        discharge_record.kalium = 4.2
        
        # Commit changes
        db.session.commit()
        
        print(f"After edit - current_weight: {discharge_record.current_weight}")
        print(f"After edit - estimated_dryweight: {discharge_record.estimated_dryweight}")
        print(f"After edit - discharge_medication: {discharge_record.discharge_medication}")
        print(f"After edit - discharge_date: {discharge_record.discharge_date}")
        print(f"After edit - ntprobnp: {discharge_record.ntprobnp}")
        print(f"After edit - kalium: {discharge_record.kalium}")
        
        print("\n✅ Edit simulation completed successfully!")
        print("Data is properly saved to database.")
        print("If fields appear empty in the form, the issue is in the template display logic.")

if __name__ == "__main__":
    test_discharge_edit()
