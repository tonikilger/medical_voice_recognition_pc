from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
db = SQLAlchemy()

class Recording(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, nullable=False)
    recording_type = db.Column(db.String(100), nullable=False)
    hospitalization_day = db.Column(db.Float, nullable=True)

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
    estimated_dryweight = db.Column(db.Float, nullable=True)

    # Voice sample (shared for all types)
    voice_sample_standardized = db.Column(db.LargeBinary, nullable=True)
    voice_sample_storytelling = db.Column(db.LargeBinary, nullable=True)
    voice_sample_vocal = db.Column(db.LargeBinary, nullable=True)

    # Date of recording
    date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    score = db.Column(db.Integer, nullable=True)

    @property
    def calculated_date(self):
        """Calculate the date based on admission date and hospitalization day"""
        if self.recording_type == 'admission':
            return self.admission_date
        
        # For daily and discharge recordings, calculate from admission date
        if self.hospitalization_day is not None:
            # Find the admission record for this patient to get the admission date
            admission_record = Recording.query.filter_by(
                patient_id=self.patient_id,
                recording_type='admission'
            ).first()
            
            if admission_record and admission_record.admission_date:
                # Calculate date by adding hospitalization_day - 1 days to admission date
                # (Day 1 = admission date, Day 2 = admission date + 1, etc.)
                return admission_record.admission_date + datetime.timedelta(days=self.hospitalization_day - 1)
        
        # Fallback to the recorded date
        return self.date.date() if self.date else None

    @property
    def formatted_calculated_date(self):
        """Return the calculated date formatted as string"""
        calc_date = self.calculated_date
        return calc_date.strftime('%Y-%m-%d') if calc_date else None

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)

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
