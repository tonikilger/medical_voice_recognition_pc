from flask import Blueprint, render_template, request, redirect, url_for
from models import Recording, db, Patient
import datetime

# Create a Blueprint
views = Blueprint('views', __name__)

# Define routes
@views.route('/')
def home():
    return render_template('home.html')

@views.route('/dashboards')
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
            "initial_weight", "initial_bp", "voice_sample",
            # KCCQ-Fragen
            "kccq1a", "kccq1b", "kccq1c", "kccq1d", "kccq1e", "kccq1f",
            "kccq2", "kccq3", "kccq4", "kccq5", "kccq6", "kccq7", "kccq8", "kccq9", "kccq10", "kccq11",
            "kccq12", "kccq13", "kccq14", "kccq15a", "kccq15b", "kccq15c", "kccq15d", "kccq16"
        ],
        "daily": [
            "recording_type", "hospitalization_day", "weight", "bp", "pulse", "voice_sample",
            "medication_changes", "kalium_daily", "natrium_daily", "kreatinin_gfr_daily", "harnstoff_daily", "hb_daily", "ntprobnp_daily"
        ],
        "discharge": [
            "recording_type", "hospitalization_day", "ntprobnp", "kalium", "natrium", "kreatinin_gfr", "harnstoff", "hb",
            "current_weight", "discharge_medication", "discharge_date", "voice_sample",
            # KCCQ-Fragen (ggf. mit anderem Prefix, falls du sie für Discharge separat speicherst)
            "kccq1a", "kccq1b", "kccq1c", "kccq1d", "kccq1e", "kccq1f",
            "kccq2", "kccq3", "kccq4", "kccq5", "kccq6", "kccq7", "kccq8", "kccq9", "kccq10", "kccq11",
            "kccq12", "kccq13", "kccq14", "kccq15a", "kccq15b", "kccq15c", "kccq15d", "kccq16"
        ]
    }

    for recording in recordings:
        rec_type = (recording.recording_type or "").lower()
        required_fields = required_fields_by_type.get(rec_type, ["recording_type", "hospitalization_day", "voice_sample"])
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
        voice_file = request.files.get('voice_sample')
        voice_sample = voice_file.read() if voice_file else None

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

        # Build the Recording object with all possible fields
        recording = Recording(
            patient_id=patient_id,
            recording_type=request.form.get('recording_type'),
            hospitalization_day=request.form.get('hospitalization_day'),

            # Admission fields
            age=request.form.get('age') or None,
            gender=request.form.get('gender') or None,
            height=request.form.get('height') or None,
            diagnosis=request.form.get('diagnosis') or None,
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
            voice_sample=voice_sample,

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
            hospitalization_day = (datetime.datetime.now().date() - first_recording.date.date()).days
    return render_template('recording.html', last_recording=last_recording, hospitalization_day=hospitalization_day, patient_id=patient_id)

@views.route('/search', methods=['GET'])
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