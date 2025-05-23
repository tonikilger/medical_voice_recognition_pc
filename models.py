
from flask_sqlalchemy import SQLAlchemy
import datetime
db = SQLAlchemy()

class Recording(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, nullable=False)
    recording_type = db.Column(db.String(100), nullable=False)
    hospitalization_day = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    systolic = db.Column(db.Float, nullable=True)
    diastolic = db.Column(db.Float, nullable=True)
    voice_sample = db.Column(db.LargeBinary, nullable=False)
    nocturnal_cough_sample = db.Column(db.LargeBinary, nullable=False)
    breathing_difficulty = db.Column(db.Integer, nullable=False)
    chest_pain = db.Column(db.Integer, nullable=False)
    fatigue_level = db.Column(db.Integer, nullable=False)
    sleep_quality = db.Column(db.Integer, nullable=False)
    additional_notes = db.Column(db.String(10000), nullable=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
