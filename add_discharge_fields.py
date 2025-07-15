#!/usr/bin/env python3
"""Add discharge-specific lab value fields to Recording model"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def add_discharge_fields():
    # Import here to avoid circular imports
    from models import Recording, db
    from flask import Flask
    from sqlalchemy import text
    
    # Create Flask app with proper config
    app = Flask(__name__)
    # Use absolute path to database file
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'database.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        print("=== ADDING DISCHARGE-SPECIFIC LAB FIELDS ===")
        
        # Add new columns to the Recording table
        try:
            # Check if columns already exist
            result = db.session.execute(text("PRAGMA table_info(recording)"))
            columns = [row[1] for row in result.fetchall()]
            
            new_columns = [
                'discharge_ntprobnp',
                'discharge_kalium',
                'discharge_natrium',
                'discharge_kreatinin_gfr',
                'discharge_harnstoff',
                'discharge_hb'
            ]
            
            for column in new_columns:
                if column not in columns:
                    print(f"Adding column: {column}")
                    if column == 'discharge_kreatinin_gfr':
                        # String field for GFR
                        db.session.execute(text(f"ALTER TABLE recording ADD COLUMN {column} TEXT"))
                    else:
                        # Numeric fields
                        db.session.execute(text(f"ALTER TABLE recording ADD COLUMN {column} REAL"))
                else:
                    print(f"Column {column} already exists")
            
            db.session.commit()
            print("✅ Successfully added discharge-specific lab fields!")
            
        except Exception as e:
            print(f"❌ Error adding columns: {e}")
            db.session.rollback()
            return False
        
        return True

if __name__ == "__main__":
    success = add_discharge_fields()
    if success:
        print("\n🎉 Migration completed successfully!")
        print("You can now use separate discharge lab values that won't overwrite admission values.")
    else:
        print("\n❌ Migration failed!")
