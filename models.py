from flask_sqlalchemy import SQLAlchemy
import datetime
db = SQLAlchemy()

class Recording(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, nullable=False)
    recording_type = db.Column(db.String(100), nullable=False)
    hospitalization_day = db.Column(db.Integer, nullable=True)

    # Admission fields
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    height = db.Column(db.Float, nullable=True)
    diagnosis = db.Column(db.String(500), nullable=True)
    medication = db.Column(db.String(2000), nullable=True)
    comorbidities = db.Column(db.String(1000), nullable=True)
    admission_date = db.Column(db.Date, nullable=True)
    ntprobnp = db.Column(db.Float, nullable=True)
    kalium = db.Column(db.Float, nullable=True)
    natrium = db.Column(db.Float, nullable=True)
    kreatinin_gfr = db.Column(db.String(100), nullable=True)
    harnstoff = db.Column(db.Float, nullable=True)
    hb = db.Column(db.Float, nullable=True)
    initial_weight = db.Column(db.Float, nullable=True)
    initial_bp = db.Column(db.String(50), nullable=True)

    # KCCQ Einzelitems (Admission/Discharge)
    kccq1a = db.Column(db.Integer, nullable=True)
    kccq1b = db.Column(db.Integer, nullable=True)
    kccq1c = db.Column(db.Integer, nullable=True)
    kccq1d = db.Column(db.Integer, nullable=True)
    kccq1e = db.Column(db.Integer, nullable=True)
    kccq1f = db.Column(db.Integer, nullable=True)
    kccq2 = db.Column(db.Integer, nullable=True)
    kccq3 = db.Column(db.Integer, nullable=True)
    kccq4 = db.Column(db.Integer, nullable=True)
    kccq5 = db.Column(db.Integer, nullable=True)
    kccq6 = db.Column(db.Integer, nullable=True)
    kccq7 = db.Column(db.Integer, nullable=True)
    kccq8 = db.Column(db.Integer, nullable=True)
    kccq9 = db.Column(db.Integer, nullable=True)
    kccq10 = db.Column(db.Integer, nullable=True)
    kccq11 = db.Column(db.Integer, nullable=True)
    kccq12 = db.Column(db.Integer, nullable=True)
    kccq13 = db.Column(db.Integer, nullable=True)
    kccq14 = db.Column(db.Integer, nullable=True)
    kccq15a = db.Column(db.Integer, nullable=True)
    kccq15b = db.Column(db.Integer, nullable=True)
    kccq15c = db.Column(db.Integer, nullable=True)
    kccq15d = db.Column(db.Integer, nullable=True)
    kccq16 = db.Column(db.Integer, nullable=True)

    # Daily fields
    weight = db.Column(db.Float, nullable=True)
    bp = db.Column(db.String(50), nullable=True)
    pulse = db.Column(db.Integer, nullable=True)
    medication_changes = db.Column(db.String(2000), nullable=True)
    kalium_daily = db.Column(db.Float, nullable=True)
    natrium_daily = db.Column(db.Float, nullable=True)
    kreatinin_gfr_daily = db.Column(db.String(100), nullable=True)
    harnstoff_daily = db.Column(db.Float, nullable=True)
    hb_daily = db.Column(db.Float, nullable=True)
    ntprobnp_daily = db.Column(db.Float, nullable=True)

    # Discharge fields
    abschluss_labor = db.Column(db.String(2000), nullable=True)
    current_weight = db.Column(db.Float, nullable=True)
    discharge_medication = db.Column(db.String(2000), nullable=True)
    discharge_date = db.Column(db.Date, nullable=True)

    # Voice sample (shared for all types)
    voice_sample = db.Column(db.LargeBinary, nullable=True)

    # Date of recording
    date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
