#!/usr/bin/env python3
"""Simple test to show discharge record fields"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_discharge_fields():
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
        print("=== DISCHARGE RECORD FIELD VALUES ===")
        
        # Find the discharge record for patient 001
        discharge_record = Recording.query.filter_by(
            patient_id=1,
            recording_type='discharge'
        ).first()
        
        if not discharge_record:
            print("❌ No discharge record found for patient 001!")
            return
            
        print(f"✅ Found discharge record (ID: {discharge_record.id})")
        print(f"Recording Type: {discharge_record.recording_type}")
        print(f"Hospitalization Day: {discharge_record.hospitalization_day}")
        print()
        
        # Check all discharge-specific fields
        discharge_fields = [
            'current_weight',
            'discharge_medication', 
            'discharge_date',
            'estimated_dryweight',
            'abschluss_labor',
            'ntprobnp',
            'kalium',
            'natrium',
            'kreatinin_gfr',
            'harnstoff',
            'hb'
        ]
        
        print("=== DISCHARGE FIELD VALUES ===")
        for field in discharge_fields:
            value = getattr(discharge_record, field, None)
            if value is not None:
                print(f"✅ {field}: {value}")
            else:
                print(f"❌ {field}: None")
        
        print()
        print("=== KCCQ FIELDS (Sample) ===")
        kccq_sample = ['kccq1a', 'kccq1b', 'kccq1c']
        for field in kccq_sample:
            value = getattr(discharge_record, field, None)
            if value is not None:
                print(f"✅ {field}: {value}")
            else:
                print(f"❌ {field}: None")
        
        print(f"\n✅ Total KCCQ Score: {discharge_record.score}")

if __name__ == "__main__":
    test_discharge_fields()
