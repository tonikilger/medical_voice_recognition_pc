#!/usr/bin/env python3
"""Debug script to check patient 001 data"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_patient_001():
    # Import here to avoid circular imports
    from models import Recording, Patient, db
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    
    # Create Flask app with proper config
    app = Flask(__name__)
    # Use absolute path to database file
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'database.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        print("=== PATIENT 001 DATA CHECK ===")
        print(f"Database path: {db_path}")
        
        # Check if patient exists
        patient = Patient.query.filter_by(id=1).first()
        if not patient:
            print("❌ Patient 001 does not exist!")
            return
        
        print(f"✅ Patient 001 exists")
        
        # Get all recordings for patient 001
        recordings = Recording.query.filter_by(patient_id=1).order_by(Recording.date).all()
        print(f"📊 Total recordings for patient 001: {len(recordings)}")
        
        for i, record in enumerate(recordings):
            print(f"\n--- Recording {i+1} ---")
            print(f"ID: {record.id}")
            print(f"Type: {record.recording_type}")
            print(f"Hospital Day: {record.hospitalization_day}")
            print(f"Date: {record.date}")
            
            # Check admission fields
            if record.recording_type == 'admission':
                print("ADMISSION DATA:")
                print(f"  Age: {record.age}")
                print(f"  Gender: {record.gender}")
                print(f"  Height: {record.height}")
                print(f"  Diagnosis: {record.diagnosis}")
                print(f"  Medication: {record.medication}")
                print(f"  Admission Date: {record.admission_date}")
                print(f"  Initial Weight: {record.initial_weight}")
                print(f"  NT-proBNP: {record.ntprobnp}")
                print(f"  Kalium: {record.kalium}")
                print(f"  KCCQ1a: {record.kccq1a}")
                print(f"  KCCQ Score: {record.score}")
            
            # Check discharge fields
            elif record.recording_type == 'discharge':
                print("DISCHARGE DATA:")
                print(f"  Current Weight: {record.current_weight}")
                print(f"  Discharge Medication: {record.discharge_medication}")
                print(f"  Discharge Date: {record.discharge_date}")
                print(f"  Estimated Dryweight: {record.estimated_dryweight}")
                print(f"  Abschluss Labor: {record.abschluss_labor}")
                print(f"  NT-proBNP: {record.ntprobnp}")
                print(f"  Kalium: {record.kalium}")
                print(f"  KCCQ1a: {record.kccq1a}")
                print(f"  KCCQ Score: {record.score}")
            
            # Check daily fields
            elif record.recording_type == 'daily':
                print("DAILY DATA:")
                print(f"  Weight: {record.weight}")
                print(f"  BP: {record.bp}")
                print(f"  Pulse: {record.pulse}")
                print(f"  Medication Changes: {record.medication_changes}")
                print(f"  Kalium Daily: {record.kalium_daily}")
            
            # Check voice samples
            voice_samples = []
            if record.voice_sample_standardized:
                voice_samples.append("standardized")
            if record.voice_sample_storytelling:
                voice_samples.append("storytelling")
            if record.voice_sample_vocal:
                voice_samples.append("vocal")
            
            print(f"  Voice Samples: {', '.join(voice_samples) if voice_samples else 'None'}")

if __name__ == "__main__":
    check_patient_001()
