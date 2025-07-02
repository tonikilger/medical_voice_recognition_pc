from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from models import Recording, db, Patient, User
import datetime

# Create a Blueprint
views = Blueprint('views', __name__)

# Define routes
@views.route('/')
def home():
    return render_template('home.html')

@views.route('/dashboards')
@login_required
def dashboards():
    patients = Patient.query.all()
    recordings = Recording.query.all()
    recordings_by_patient = {}
    complete_records_by_patient = {}
    incomplete_records_by_patient = {}
    required_fields_by_type = {
        "admission": [
            "recording_type", "hospitalization_day", "age", "gender", "height", "diagnosis", "medication", "comorbidities",
            "admission_date", "ntprobnp", "kalium", "natrium", "kreatinin_gfr", "harnstoff", "hb",
            "initial_weight", "initial_bp", "voice_sample_standardized",
            # KCCQ-Fragen
            "kccq1a", "kccq1b", "kccq1c", "kccq1d", "kccq1e", "kccq1f",
            "kccq2", "kccq3", "kccq4", "kccq5", "kccq6", "kccq7", "kccq8", "kccq9", "kccq10", "kccq11",
            "kccq12", "kccq13", "kccq14", "kccq15a", "kccq15b", "kccq15c", "kccq15d", "kccq16"
        ],
        "daily": [
            "recording_type", "hospitalization_day", "weight", "bp", "pulse", "voice_sample_standardized",
            "medication_changes", "kalium_daily", "natrium_daily", "kreatinin_gfr_daily", "harnstoff_daily", "hb_daily", "ntprobnp_daily"
        ],
        "discharge": [
            "recording_type", "hospitalization_day", "ntprobnp", "kalium", "natrium", "kreatinin_gfr", "harnstoff", "hb",
            "current_weight", "discharge_medication", "discharge_date", "voice_sample_standardized",
            # KCCQ-Fragen (ggf. mit anderem Prefix, falls du sie für Discharge separat speicherst)
            "kccq1a", "kccq1b", "kccq1c", "kccq1d", "kccq1e", "kccq1f",
            "kccq2", "kccq3", "kccq4", "kccq5", "kccq6", "kccq7", "kccq8", "kccq9", "kccq10", "kccq11",
            "kccq12", "kccq13", "kccq14", "kccq15a", "kccq15b", "kccq15c", "kccq15d", "kccq16"
        ]
    }

    for recording in recordings:
        rec_type = (recording.recording_type or "").lower()
        required_fields = required_fields_by_type.get(rec_type, ["recording_type", "hospitalization_day", "voice_sample_standardized"])
        is_complete = True
        for field in required_fields:
            value = getattr(recording, field, None)
            if value in (None, '', 0):
                is_complete = False
                break

        recordings_by_patient.setdefault(recording.patient_id, []).append(recording)
        if is_complete:
            complete_records_by_patient.setdefault(recording.patient_id, []).append(recording)
        else:
            incomplete_records_by_patient.setdefault(recording.patient_id, []).append(recording)

    return render_template(
        'dashboards.html',
        patients=patients,
        recordings_by_patient=recordings_by_patient,
        complete_records_by_patient=complete_records_by_patient,
        incomplete_records_by_patient=incomplete_records_by_patient
    )

@views.route('/recording', methods=['GET', 'POST'])
@login_required
def recording():
    def parse_date(date_str):
        if date_str:
            try:
                return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return None
        return None

    if request.method == 'POST':
        patient_id = request.form.get('patient_id')
        patient = Patient.query.filter_by(id=patient_id).first()
        if not patient:
            new_patient = Patient(id=patient_id)
            db.session.add(new_patient)
            db.session.commit()

        # Voice sample
        voice_file = request.files.get('voice_sample_standardized')
        voice_sample_standardized = voice_file.read() if voice_file else None

        story_file = request.files.get('voice_sample_storytelling')
        story_sample = story_file.read() if story_file else None

        # Score berechnen (Summe aller KCCQ-Items)
        kccq_fields = [
            'kccq1a', 'kccq1b', 'kccq1c', 'kccq1d', 'kccq1e', 'kccq1f',
            'kccq2', 'kccq3', 'kccq4', 'kccq5', 'kccq6', 'kccq7', 'kccq8', 'kccq9', 'kccq10', 'kccq11',
            'kccq12', 'kccq13', 'kccq14', 'kccq15a', 'kccq15b', 'kccq15c', 'kccq15d', 'kccq16'
        ]
        score = 0
        for field in kccq_fields:
            value = request.form.get(field)
            if value and value.isdigit():
                score += int(value)

        admission_date_str = request.form.get('admission_date') or None
        admission_date = parse_date(admission_date_str)

        discharge_date_str = request.form.get('discharge_date') or None
        discharge_date = parse_date(discharge_date_str)

        recordings = Recording.query.filter_by(patient_id=patient_id).order_by(Recording.date).all()
        if recordings:
            first_recording = recordings[0]
            last_recording = recordings[-1]
            hospitalization_day = (datetime.datetime.now().date() - first_recording.date.date()).days + 1
        else:
            hospitalization_day = 1    

        diagnosis = request.form.getlist('diagnosis')
        diagnosis_str = ', '.join(diagnosis) if diagnosis else None

        # Build the Recording object with all possible fields
        recording = Recording(
            patient_id=patient_id,
            recording_type=request.form.get('recording_type'),
            hospitalization_day=hospitalization_day,

            # Admission fields
            age=request.form.get('age') or None,
            gender=request.form.get('gender') or None,
            height=request.form.get('height') or None,
            diagnosis=diagnosis_str,
            medication=request.form.get('medication') or None,
            comorbidities=request.form.get('comorbidities') or None,
            admission_date=admission_date,
            ntprobnp=request.form.get('ntprobnp') or None,
            kalium=request.form.get('kalium') or None,
            natrium=request.form.get('natrium') or None,
            kreatinin_gfr=request.form.get('kreatinin_gfr') or None,
            harnstoff=request.form.get('harnstoff') or None,
            hb=request.form.get('hb') or None,
            initial_weight=request.form.get('initial_weight') or None,
            initial_bp=request.form.get('initial_bp') or None,

            # KCCQ Einzelitems
            kccq1a=request.form.get('kccq1a') or None,
            kccq1b=request.form.get('kccq1b') or None,
            kccq1c=request.form.get('kccq1c') or None,
            kccq1d=request.form.get('kccq1d') or None,
            kccq1e=request.form.get('kccq1e') or None,
            kccq1f=request.form.get('kccq1f') or None,
            kccq2=request.form.get('kccq2') or None,
            kccq3=request.form.get('kccq3') or None,
            kccq4=request.form.get('kccq4') or None,
            kccq5=request.form.get('kccq5') or None,
            kccq6=request.form.get('kccq6') or None,
            kccq7=request.form.get('kccq7') or None,
            kccq8=request.form.get('kccq8') or None,
            kccq9=request.form.get('kccq9') or None,
            kccq10=request.form.get('kccq10') or None,
            kccq11=request.form.get('kccq11') or None,
            kccq12=request.form.get('kccq12') or None,
            kccq13=request.form.get('kccq13') or None,
            kccq14=request.form.get('kccq14') or None,
            kccq15a=request.form.get('kccq15a') or None,
            kccq15b=request.form.get('kccq15b') or None,
            kccq15c=request.form.get('kccq15c') or None,
            kccq15d=request.form.get('kccq15d') or None,
            kccq16=request.form.get('kccq16') or None,

            # Daily fields
            weight=request.form.get('weight') or None,
            bp=request.form.get('bp') or None,
            pulse=request.form.get('pulse') or None,
            medication_changes=request.form.get('medication_changes') or None,
            kalium_daily=request.form.get('kalium_daily') or None,
            natrium_daily=request.form.get('natrium_daily') or None,
            kreatinin_gfr_daily=request.form.get('kreatinin_gfr_daily') or None,
            harnstoff_daily=request.form.get('harnstoff_daily') or None,
            hb_daily=request.form.get('hb_daily') or None,
            ntprobnp_daily=request.form.get('ntprobnp_daily') or None,

            # Discharge fields
            abschluss_labor=request.form.get('abschluss_labor') or None,
            current_weight=request.form.get('current_weight') or None,
            discharge_medication=request.form.get('discharge_medication') or None,
            discharge_date=discharge_date or None,

            # Voice sample
            voice_sample_standardized=voice_sample_standardized,
            voice_sample_storytelling=story_sample,  # <-- add this field to your model as well!

            # Date of recording
            date=datetime.datetime.now(),
            score=score
        )

        db.session.add(recording)
        db.session.commit()
        return redirect(url_for('views.dashboards'))

    # GET request
    patient_id = request.args.get('patient_id')
    last_recording = None
    hospitalization_day = ''
    if patient_id:
        recordings = Recording.query.filter_by(patient_id=patient_id).order_by(Recording.date).all()
        if recordings:
            first_recording = recordings[0]
            last_recording = recordings[-1]
            hospitalization_day = (datetime.datetime.now().date() - first_recording.date.date()).days + 1
    return render_template(
        'recording.html',
        last_recording=last_recording,
        hospitalization_day=hospitalization_day,
        patient_id=patient_id,
        datetime=datetime  # <--- hinzufügen
    )

@views.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('query', '').strip()  # Get the search query from the URL
    records = []
    patient = None

    if query.isdigit():  # Ensure the query is numeric
        patient = Patient.query.filter_by(id=int(query)).first()  # Find the patient by ID
        if patient:
            records = Recording.query.filter_by(patient_id=patient.id).order_by(Recording.hospitalization_day.asc()).all()
        else:
            records = []

    return render_template('search.html', patient=patient, records=records, query=query)

@views.route('/delete_recording/<int:recording_id>', methods=['POST'])
def delete_recording(recording_id):
    recording = Recording.query.get_or_404(recording_id)
    patient_id = recording.patient_id
    db.session.delete(recording)
    db.session.commit()
    # Prüfe, ob der Patient noch weitere Recordings hat
    remaining = Recording.query.filter_by(patient_id=patient_id).count()
    if remaining == 0:
        patient = Patient.query.get(patient_id)
        if patient:
            db.session.delete(patient)
            db.session.commit()
    return redirect(request.referrer or url_for('views.dashboards'))

@views.route('/edit_recording/<int:recording_id>', methods=['GET', 'POST'])
def edit_recording(recording_id):
    recording = Recording.query.get_or_404(recording_id)
    def parse_date(date_str):
        if date_str:
            try:
                return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return None
        return None

    if request.method == 'POST':
        # Admission fields
        recording.age = request.form.get('age') or None
        recording.gender = request.form.get('gender') or None
        recording.height = request.form.get('height') or None
        diagnosis = request.form.getlist('diagnosis')
        recording.diagnosis = ', '.join(diagnosis) if diagnosis else None
        recording.medication = request.form.get('medication') or None
        recording.comorbidities = request.form.get('comorbidities') or None
        recording.admission_date = parse_date(request.form.get('admission_date'))
        recording.ntprobnp = request.form.get('ntprobnp') or None
        recording.kalium = request.form.get('kalium') or None
        recording.natrium = request.form.get('natrium') or None
        recording.kreatinin_gfr = request.form.get('kreatinin_gfr') or None
        recording.harnstoff = request.form.get('harnstoff') or None
        recording.hb = request.form.get('hb') or None
        recording.initial_weight = request.form.get('initial_weight') or None
        recording.initial_bp = request.form.get('initial_bp') or None

        # KCCQ fields
        for field in [
            'kccq1a', 'kccq1b', 'kccq1c', 'kccq1d', 'kccq1e', 'kccq1f',
            'kccq2', 'kccq3', 'kccq4', 'kccq5', 'kccq6', 'kccq7', 'kccq8', 'kccq9', 'kccq10', 'kccq11',
            'kccq12', 'kccq13', 'kccq14', 'kccq15a', 'kccq15b', 'kccq15c', 'kccq15d', 'kccq16'
        ]:
            setattr(recording, field, request.form.get(field) or None)

        # Daily fields
        recording.weight = request.form.get('weight') or None
        recording.bp = request.form.get('bp') or None
        recording.pulse = request.form.get('pulse') or None
        recording.medication_changes = request.form.get('medication_changes') or None
        recording.kalium_daily = request.form.get('kalium_daily') or None
        recording.natrium_daily = request.form.get('natrium_daily') or None
        recording.kreatinin_gfr_daily = request.form.get('kreatinin_gfr_daily') or None
        recording.harnstoff_daily = request.form.get('harnstoff_daily') or None
        recording.hb_daily = request.form.get('hb_daily') or None
        recording.ntprobnp_daily = request.form.get('ntprobnp_daily') or None

        # Discharge fields
        recording.abschluss_labor = request.form.get('abschluss_labor') or None
        recording.current_weight = request.form.get('current_weight') or None
        recording.discharge_medication = request.form.get('discharge_medication') or None
        recording.discharge_date = parse_date(request.form.get('discharge_date'))

        # Voice samples (only update if a new file is uploaded)
        voice_file = request.files.get('voice_sample_standardized')
        if voice_file and voice_file.filename:
            recording.voice_sample_standardized = voice_file.read()
        story_file = request.files.get('voice_sample_storytelling')
        if story_file and story_file.filename:
            recording.voice_sample_storytelling = story_file.read()

        # Score calculation
        score = 0
        for field in [
            'kccq1a', 'kccq1b', 'kccq1c', 'kccq1d', 'kccq1e', 'kccq1f',
            'kccq2', 'kccq3', 'kccq4', 'kccq5', 'kccq6', 'kccq7', 'kccq8', 'kccq9', 'kccq10', 'kccq11',
            'kccq12', 'kccq13', 'kccq14', 'kccq15a', 'kccq15b', 'kccq15c', 'kccq15d', 'kccq16'
        ]:
            value = request.form.get(field)
            if value and value.isdigit():
                score += int(value)
        recording.score = score

        db.session.commit()
        return redirect(url_for('views.search', query=recording.patient_id))
    # GET: Render the form with prefilled values
    return render_template(
        'recording.html',
        last_recording=recording,
        hospitalization_day=recording.hospitalization_day,
        patient_id=recording.patient_id,
        datetime=datetime
    )

login_blueprint = Blueprint('login', __name__)

@login_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for('views.dashboards'))
        flash('Login fehlgeschlagen!')
    return render_template('login.html')

@login_blueprint.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login.login'))