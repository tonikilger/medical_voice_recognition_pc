#!/usr/bin/env python3
"""
Debug script to check if daily recording for patient ID 001, day 2 exists in database
"""

import sqlite3
import os
from datetime import datetime

# Database path
DB_PATH = os.path.join('instance', 'database.db')

def check_daily_recording():
    """Check if daily recording exists for patient ID 001, day 2"""
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # First, check the table structure
        cursor.execute("PRAGMA table_info(recording)")
        columns = cursor.fetchall()
        print("=== Database Schema for 'recording' table ===")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        print()
        
        # Query for daily recording with patient_id 001 and hospitalization_day 2
        query = """
        SELECT 
            id, patient_id, hospitalization_day, recording_type, date,
            voice_sample_standardized, voice_sample_storytelling, voice_sample_vocal,
            CASE 
                WHEN voice_sample_standardized IS NOT NULL THEN 'YES' 
                ELSE 'NO' 
            END as has_standardized,
            CASE 
                WHEN voice_sample_storytelling IS NOT NULL THEN 'YES' 
                ELSE 'NO' 
            END as has_storytelling,
            CASE 
                WHEN voice_sample_vocal IS NOT NULL THEN 'YES' 
                ELSE 'NO' 
            END as has_vocal
        FROM recording 
        WHERE patient_id = 1 AND hospitalization_day = 2 AND recording_type = 'daily'
        ORDER BY date DESC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        print(f"=== Daily Recording Check for Patient ID 001, Day 2 ===")
        print(f"Database: {DB_PATH}")
        print(f"Query executed at: {datetime.now()}")
        print()
        
        if results:
            print(f"Found {len(results)} daily recording(s) for Patient ID 001, Day 2:")
            print("-" * 80)
            
            for row in results:
                (rec_id, patient_id, day, rec_type, date, 
                 voice_std, voice_story, voice_vocal, 
                 has_std, has_story, has_vocal) = row
                
                print(f"Record ID: {rec_id}")
                print(f"Patient ID: {patient_id}")
                print(f"Hospitalization Day: {day}")
                print(f"Type: {rec_type}")
                print(f"Date: {date}")
                print(f"Voice Samples:")
                print(f"  - Standardized: {has_std}")
                print(f"  - Storytelling: {has_story}")
                print(f"  - Vocal: {has_vocal}")
                print("-" * 80)
                
        else:
            print("No daily recording found for Patient ID 001, Day 2")
        
        # Also check if there are any recordings at all for patient 001
        cursor.execute("SELECT COUNT(*) FROM recording WHERE patient_id = 1")
        total_count = cursor.fetchone()[0]
        print(f"\nTotal recordings for Patient ID 001: {total_count}")
        
        # Show all recordings for patient 001
        if total_count > 0:
            cursor.execute("""
                SELECT recording_type, hospitalization_day, date, 
                       CASE WHEN voice_sample_standardized IS NOT NULL THEN 'YES' ELSE 'NO' END,
                       CASE WHEN voice_sample_storytelling IS NOT NULL THEN 'YES' ELSE 'NO' END,
                       CASE WHEN voice_sample_vocal IS NOT NULL THEN 'YES' ELSE 'NO' END
                FROM recording 
                WHERE patient_id = 1 
                ORDER BY recording_type, hospitalization_day, date
            """)
            all_recordings = cursor.fetchall()
            
            print(f"\nAll recordings for Patient ID 001:")
            print("Type\t\tDay\tDate\t\t\tStd\tStory\tVocal")
            print("-" * 70)
            for rec in all_recordings:
                rec_type, day, date, std, story, vocal = rec
                print(f"{rec_type}\t\t{day}\t{date}\t{std}\t{story}\t{vocal}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_daily_recording()