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

    for recording in recordings:
        # Define which fields are required for a complete record
        required_fields = [
            recording.recording_type,
            recording.hospitalization_day,
            recording.weight,
            recording.systolic,
            recording.diastolic,
            recording.voice_sample,
            recording.nocturnal_cough_sample,
            recording.breathing_difficulty,
            recording.chest_pain,
            recording.fatigue_level,
            recording.sleep_quality,

            # Add other required fields here if needed
        ]
        is_complete = all(field not in (None, '', 0) for field in required_fields)
        # Group by patient
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
    if request.method == 'POST':
        patient_id = request.form.get('patient_id')
        patient = Patient.query.filter_by(id=patient_id).first()
        if not patient:
            new_patient = Patient(id=patient_id)
            db.session.add(new_patient)
            db.session.commit()

        voice_file = request.files.get('voice_sample')
        cough_file = request.files.get('nocturnal_cough_sample')
        recording = Recording(
            patient_id=patient_id,
            recording_type=request.form.get('recording_type'),
            hospitalization_day=request.form.get('hospitalization_day'),
            weight=request.form.get('weight'),
            systolic=request.form.get('systolic_bp') if request.form.get('systolic_bp') else None,
            diastolic=request.form.get('diastolic_bp') if request.form.get('diastolic_bp') else None,
            voice_sample=voice_file.read() if voice_file else None,
            nocturnal_cough_sample=cough_file.read() if cough_file else None,
            breathing_difficulty=request.form.get('breathing_difficulty'),
            chest_pain=request.form.get('chest_pain'),
            fatigue_level=request.form.get('fatigue_level'),
            sleep_quality=request.form.get('sleep_quality'),
            additional_notes=request.form.get('additional_notes'),
            date=datetime.datetime.now()
        )
        db.session.add(recording)
        db.session.commit()
        return render_template('recording.html')

    # GET request
    patient_id = request.args.get('patient_id')
    last_recording = None
    hospitalization_day = ''
    if patient_id:
        # Get last and first recording for prefill
        recordings = Recording.query.filter_by(patient_id=patient_id).order_by(Recording.date).all()
        if recordings:
            first_recording = recordings[0]
            last_recording = recordings[-1]
            # Calculate hospitalization day as days since first recording + 1
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