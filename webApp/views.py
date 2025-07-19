from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, jsonify, send_file
from flask_login import login_user, logout_user, login_required, current_user
from webApp.models import Recording, db, Patient, User
import datetime
import json
import csv
import io
import os
import zipfile
import tempfile
import base64
from functools import wraps

# Create a Blueprint
views = Blueprint('views', __name__)
        
def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin privileges required.')
            return redirect(url_for('login.login'))
        return f(*args, **kwargs)
    return decorated_function

# Audio format detection utilities
def detect_audio_format(audio_data):
    """Detect audio format based on file header"""
    if not audio_data or len(audio_data) < 12:
        return 'webm'
    
    header = audio_data[:12]
    extended_header = audio_data[:20] if len(audio_data) >= 20 else header
    
    # WebM/Matroska format
    if b'matroska' in header.lower() or audio_data.startswith(b'\x1a\x45\xdf\xa3'):
        return 'webm'
    # Ogg format
    elif header.startswith(b'OggS'):
        return 'ogg'
    # MP3 format
    elif header.startswith(b'ID3') or header.startswith(b'\xff\xfb'):
        return 'mp3'
    # WAV format
    elif header.startswith(b'RIFF') and b'WAVE' in header:
        return 'wav'
    # MP4/M4A/AAC format (iOS common formats)
    elif b'ftyp' in header or header.startswith(b'\x00\x00\x00'):
        # Check for specific MP4/M4A subtypes
        if b'M4A ' in extended_header or b'mp42' in extended_header:
            return 'm4a'
        elif b'mp4' in extended_header.lower():
            return 'mp4'
        else:
            return 'm4a'  # Default for iOS audio
    # AAC format (raw AAC without container)
    elif header.startswith(b'\xff\xf1') or header.startswith(b'\xff\xf9'):
        return 'aac'
    
    # Default fallback
    return 'webm'

def export_patient_data_for_ai(patient_id):
    """Export patient data in AI-friendly format with metadata"""
    recordings = Recording.query.filter_by(patient_id=patient_id).order_by(Recording.hospitalization_day).all()
    
    if not recordings:
        return None
    
    # Structure data for AI processing
    patient_data = {
        'patient_id': patient_id,
        'admission_data': {},
        'daily_data': [],
        'discharge_data': {},
        'audio_files': {},
        'metadata': {
            'total_recordings': len(recordings),
            'hospitalization_days': [],
            'export_timestamp': datetime.datetime.now().isoformat(),
            'data_format_version': '1.0'
        }
    }
    
    for recording in recordings:
        patient_data['metadata']['hospitalization_days'].append(recording.hospitalization_day)
        
        # Common fields for all recording types
        common_data = {
            'recording_id': recording.id,
            'hospitalization_day': recording.hospitalization_day,
            'date': recording.formatted_calculated_date,
            'kccq_total_score': recording.score,
            'voice_samples_available': {
                'standardized': recording.voice_sample_standardized is not None,
                'storytelling': recording.voice_sample_storytelling is not None,
                'vocal': recording.voice_sample_vocal is not None
            }
        }
        
        if recording.recording_type == 'admission':
            patient_data['admission_data'] = {
                **common_data,
                'demographics': {
                    'age': recording.age,
                    'gender': recording.gender,
                    'height': recording.height
                },
                'clinical_data': {
                    'diagnosis': recording.diagnosis,
                    'medication': recording.medication,
                    'comorbidities': recording.comorbidities,
                    'admission_date': recording.admission_date.isoformat() if recording.admission_date else None,
                    'initial_weight': recording.initial_weight,
                    'initial_bp': recording.initial_bp
                },
                'lab_values': {
                    'ntprobnp': recording.ntprobnp,
                    'kalium': recording.kalium,
                    'natrium': recording.natrium,
                    'kreatinin_gfr': recording.kreatinin_gfr,
                    'harnstoff': recording.harnstoff,
                    'hb': recording.hb
                },
                'kccq_scores': {
                    'physical_limitation': {
                        'kccq1a': recording.kccq1a, 'kccq1b': recording.kccq1b,
                        'kccq1c': recording.kccq1c, 'kccq1d': recording.kccq1d,
                        'kccq1e': recording.kccq1e, 'kccq1f': recording.kccq1f
                    },
                    'symptom_stability': {'kccq2': recording.kccq2},
                    'symptom_frequency': {
                        'kccq3': recording.kccq3, 'kccq4': recording.kccq4,
                        'kccq5': recording.kccq5, 'kccq6': recording.kccq6,
                        'kccq7': recording.kccq7, 'kccq8': recording.kccq8
                    },
                    'symptom_burden': {
                        'kccq9': recording.kccq9, 'kccq10': recording.kccq10,
                        'kccq11': recording.kccq11, 'kccq12': recording.kccq12
                    },
                    'self_efficacy': {'kccq13': recording.kccq13, 'kccq14': recording.kccq14},
                    'quality_of_life': {
                        'kccq15a': recording.kccq15a, 'kccq15b': recording.kccq15b,
                        'kccq15c': recording.kccq15c, 'kccq15d': recording.kccq15d
                    },
                    'social_limitation': {'kccq16': recording.kccq16}
                }
            }
            
        elif recording.recording_type == 'daily':
            daily_entry = {
                **common_data,
                'vitals': {
                    'weight': recording.weight,
                    'bp': recording.bp,
                    'pulse': recording.pulse
                },
                'treatment': {
                    'medication_changes': recording.medication_changes
                },
                'lab_values': {
                    'kalium_daily': recording.kalium_daily,
                    'natrium_daily': recording.natrium_daily,
                    'kreatinin_gfr_daily': recording.kreatinin_gfr_daily,
                    'harnstoff_daily': recording.harnstoff_daily,
                    'hb_daily': recording.hb_daily,
                    'ntprobnp_daily': recording.ntprobnp_daily
                }
            }
            patient_data['daily_data'].append(daily_entry)
            
        elif recording.recording_type == 'discharge':
            patient_data['discharge_data'] = {
                **common_data,
                'clinical_data': {
                    'current_weight': recording.current_weight,
                    'discharge_medication': recording.discharge_medication,
                    'discharge_date': recording.discharge_date.isoformat() if recording.discharge_date else None,
                    'estimated_dryweight': recording.estimated_dryweight,
                    'abschluss_labor': recording.abschluss_labor
                },
                'lab_values': {
                    'ntprobnp': recording.ntprobnp,
                    'kalium': recording.kalium,
                    'natrium': recording.natrium,
                    'kreatinin_gfr': recording.kreatinin_gfr,
                    'harnstoff': recording.harnstoff,
                    'hb': recording.hb
                },
                'kccq_scores': {
                    'physical_limitation': {
                        'kccq1a': recording.kccq1a, 'kccq1b': recording.kccq1b,
                        'kccq1c': recording.kccq1c, 'kccq1d': recording.kccq1d,
                        'kccq1e': recording.kccq1e, 'kccq1f': recording.kccq1f
                    },
                    'symptom_stability': {'kccq2': recording.kccq2},
                    'symptom_frequency': {
                        'kccq3': recording.kccq3, 'kccq4': recording.kccq4,
                        'kccq5': recording.kccq5, 'kccq6': recording.kccq6,
                        'kccq7': recording.kccq7, 'kccq8': recording.kccq8
                    },
                    'symptom_burden': {
                        'kccq9': recording.kccq9, 'kccq10': recording.kccq10,
                        'kccq11': recording.kccq11, 'kccq12': recording.kccq12
                    },
                    'self_efficacy': {'kccq13': recording.kccq13, 'kccq14': recording.kccq14},
                    'quality_of_life': {
                        'kccq15a': recording.kccq15a, 'kccq15b': recording.kccq15b,
                        'kccq15c': recording.kccq15c, 'kccq15d': recording.kccq15d
                    },
                    'social_limitation': {'kccq16': recording.kccq16}
                }
            }
        
        # Audio file metadata (files will be included separately in zip)
        audio_key = f"{recording.recording_type}_day_{recording.hospitalization_day}"
        patient_data['audio_files'][audio_key] = {}
        
        if recording.voice_sample_standardized:
            format_ext = detect_audio_format(recording.voice_sample_standardized)
            patient_data['audio_files'][audio_key]['standardized'] = {
                'filename': f"patient_{patient_id}_{audio_key}_standardized.{format_ext}",
                'size_bytes': len(recording.voice_sample_standardized),
                'format': format_ext
            }
        
        if recording.voice_sample_storytelling:
            format_ext = detect_audio_format(recording.voice_sample_storytelling)
            patient_data['audio_files'][audio_key]['storytelling'] = {
                'filename': f"patient_{patient_id}_{audio_key}_storytelling.{format_ext}",
                'size_bytes': len(recording.voice_sample_storytelling),
                'format': format_ext
            }
        
        if recording.voice_sample_vocal:
            format_ext = detect_audio_format(recording.voice_sample_vocal)
            patient_data['audio_files'][audio_key]['vocal'] = {
                'filename': f"patient_{patient_id}_{audio_key}_vocal.{format_ext}",
                'size_bytes': len(recording.voice_sample_vocal),
                'format': format_ext
            }
    
    return patient_data

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

    # First, create a mapping of patient_id to admission records to get initial_weight
    admission_data_by_patient = {}
    for recording in recordings:
        if recording.recording_type == 'admission':
            admission_data_by_patient[recording.patient_id] = {
                'initial_weight': recording.initial_weight,
                'initial_bp': recording.initial_bp,
                'admission_date': recording.admission_date
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

        # Add initial_weight from admission record if this is a daily or discharge record
        if recording.recording_type in ['daily', 'discharge'] and recording.patient_id in admission_data_by_patient:
            admission_data = admission_data_by_patient[recording.patient_id]
            if not recording.initial_weight:
                recording.initial_weight = admission_data['initial_weight']
            if not recording.initial_bp:
                recording.initial_bp = admission_data['initial_bp']
            if not recording.admission_date:
                recording.admission_date = admission_data['admission_date']

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

        # Get recording type first
        recording_type = request.form.get('recording_type')
        
        # Check if a recording of this type already exists for this patient
        existing_recording = Recording.query.filter_by(
            patient_id=patient_id,
            recording_type=recording_type
        ).first()
        
        if existing_recording:
            # Update existing recording instead of creating new one
            recording = existing_recording
        else:
            # Create new recording
            recording = Recording(
                patient_id=patient_id,
                recording_type=recording_type,
                date=datetime.datetime.now()
            )

        # Voice sample names are now prefixed based on recording type
        prefix = f"{recording_type}_" if recording_type else ""
        
        voice_file = request.files.get(f'{prefix}voice_sample_standardized')
        voice_sample_standardized = voice_file.read() if voice_file and voice_file.filename else None

        story_file = request.files.get(f'{prefix}voice_sample_storytelling')
        story_sample = story_file.read() if story_file and story_file.filename else None

        vocal_file = request.files.get(f'{prefix}voice_sample_vocal')
        vocal_sample = vocal_file.read() if vocal_file and vocal_file.filename else None

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
        admission_date = parse_date(admission_date_str) if recording_type == 'admission' else None

        discharge_date_str = request.form.get('discharge_date') or None
        discharge_date = parse_date(discharge_date_str) if recording_type == 'discharge' else None

        # Calculate hospitalization_day properly for each recording type
        recordings = Recording.query.filter_by(patient_id=patient_id).order_by(Recording.date).all()
        
        if recording_type == 'admission':
            hospitalization_day = 1
        elif recording_type == 'discharge':
            # For discharge, use the form value or calculate from admission date
            hospitalization_day_form = request.form.get('hospitalization_day')
            if hospitalization_day_form:
                hospitalization_day = int(hospitalization_day_form)
            else:
                # Find admission record to calculate discharge day
                admission_record = Recording.query.filter_by(
                    patient_id=patient_id,
                    recording_type='admission'
                ).first()
                if admission_record and admission_record.admission_date and discharge_date:
                    hospitalization_day = (discharge_date - admission_record.admission_date).days + 1
                else:
                    hospitalization_day = len(recordings) + 1
        else:  # daily
            if recordings:
                hospitalization_day = len(recordings) + 1
            else:
                hospitalization_day = 1    

        diagnosis = request.form.getlist('diagnosis')
        diagnosis_str = ', '.join(diagnosis) if diagnosis else None

        # Only process KCCQ fields for admission and discharge recordings
        kccq_fields = {}
        if recording_type in ['admission', 'discharge']:
            kccq_fields = {
                'kccq1a': request.form.get('kccq1a') or None,
                'kccq1b': request.form.get('kccq1b') or None,
                'kccq1c': request.form.get('kccq1c') or None,
                'kccq1d': request.form.get('kccq1d') or None,
                'kccq1e': request.form.get('kccq1e') or None,
                'kccq1f': request.form.get('kccq1f') or None,
                'kccq2': request.form.get('kccq2') or None,
                'kccq3': request.form.get('kccq3') or None,
                'kccq4': request.form.get('kccq4') or None,
                'kccq5': request.form.get('kccq5') or None,
                'kccq6': request.form.get('kccq6') or None,
                'kccq7': request.form.get('kccq7') or None,
                'kccq8': request.form.get('kccq8') or None,
                'kccq9': request.form.get('kccq9') or None,
                'kccq10': request.form.get('kccq10') or None,
                'kccq11': request.form.get('kccq11') or None,
                'kccq12': request.form.get('kccq12') or None,
                'kccq13': request.form.get('kccq13') or None,
                'kccq14': request.form.get('kccq14') or None,
                'kccq15a': request.form.get('kccq15a') or None,
                'kccq15b': request.form.get('kccq15b') or None,
                'kccq15c': request.form.get('kccq15c') or None,
                'kccq15d': request.form.get('kccq15d') or None,
                'kccq16': request.form.get('kccq16') or None,
            }

        # Update the Recording object with all possible fields
        recording.hospitalization_day = hospitalization_day

        # Admission fields
        recording.age = request.form.get('age') or None
        recording.gender = request.form.get('gender') or None
        recording.height = request.form.get('height') or None
        recording.diagnosis = diagnosis_str
        recording.medication = request.form.get('medication') or None
        recording.comorbidities = request.form.get('comorbidities') or None
        recording.admission_date = admission_date
        recording.ntprobnp = request.form.get('ntprobnp') or None
        recording.kalium = request.form.get('kalium') or None
        recording.natrium = request.form.get('natrium') or None
        recording.kreatinin_gfr = request.form.get('kreatinin_gfr') or None
        recording.harnstoff = request.form.get('harnstoff') or None
        recording.hb = request.form.get('hb') or None
        recording.initial_weight = request.form.get('initial_weight') or None
        recording.initial_bp = request.form.get('initial_bp') or None

        # KCCQ fields (only for admission/discharge)
        if recording_type in ['admission', 'discharge']:
            for field, value in kccq_fields.items():
                setattr(recording, field, value)

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
        recording.discharge_date = discharge_date or None
        recording.estimated_dryweight = request.form.get('estimated_dryweight') or None
        
        # Discharge-specific lab values (separate from admission values)
        if recording_type == 'discharge':
            recording.discharge_ntprobnp = request.form.get('discharge_ntprobnp') or None
            recording.discharge_kalium = request.form.get('discharge_kalium') or None
            recording.discharge_natrium = request.form.get('discharge_natrium') or None
            recording.discharge_kreatinin_gfr = request.form.get('discharge_kreatinin_gfr') or None
            recording.discharge_harnstoff = request.form.get('discharge_harnstoff') or None
            recording.discharge_hb = request.form.get('discharge_hb') or None

        # Voice sample (only update if new files are uploaded)
        if voice_sample_standardized:
            recording.voice_sample_standardized = voice_sample_standardized
        if story_sample:
            recording.voice_sample_storytelling = story_sample
        if vocal_sample:
            recording.voice_sample_vocal = vocal_sample

        # Score
        recording.score = score

        # Only add to session if it's a new recording
        if not existing_recording:
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
        recording.estimated_dryweight = request.form.get('estimated_dryweight') or None
        
        # Discharge-specific lab values (separate from admission values)
        if recording.recording_type == 'discharge':
            recording.discharge_ntprobnp = request.form.get('discharge_ntprobnp') or None
            recording.discharge_kalium = request.form.get('discharge_kalium') or None
            recording.discharge_natrium = request.form.get('discharge_natrium') or None
            recording.discharge_kreatinin_gfr = request.form.get('discharge_kreatinin_gfr') or None
            recording.discharge_harnstoff = request.form.get('discharge_harnstoff') or None
            recording.discharge_hb = request.form.get('discharge_hb') or None

        # Voice samples (only update if a new file is uploaded)
        # Voice sample names are prefixed based on recording type
        prefix = f"{recording.recording_type}_" if recording.recording_type else ""

        voice_file = request.files.get(f'{prefix}voice_sample_standardized')
        if voice_file and voice_file.filename:
            recording.voice_sample_standardized = voice_file.read()
        
        story_file = request.files.get(f'{prefix}voice_sample_storytelling')
        if story_file and story_file.filename:
            recording.voice_sample_storytelling = story_file.read()
            
        vocal_file = request.files.get(f'{prefix}voice_sample_vocal')
        if vocal_file and vocal_file.filename:
            recording.voice_sample_vocal = vocal_file.read()

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

@views.route('/voice_sample/<int:recording_id>/<sample_type>')
@login_required
def get_voice_sample(recording_id, sample_type):
    """Serve voice sample files"""
    recording = Recording.query.get_or_404(recording_id)
    
    if sample_type == 'standardized':
        voice_data = recording.voice_sample_standardized
    elif sample_type == 'storytelling':
        voice_data = recording.voice_sample_storytelling
    elif sample_type == 'vocal':
        voice_data = recording.voice_sample_vocal
    else:
        return "Invalid sample type", 400
    
    if not voice_data:
        return "No voice sample found", 404
    
    return Response(
        voice_data,
        mimetype='audio/webm',
        headers={
            'Content-Disposition': f'inline; filename="{sample_type}_sample.webm"'
        }
    )

@views.route('/delete_voice_sample/<int:recording_id>/<sample_type>', methods=['POST'])
@login_required
def delete_voice_sample(recording_id, sample_type):
    """Delete a specific voice sample"""
    recording = Recording.query.get_or_404(recording_id)
    
    if sample_type == 'standardized':
        recording.voice_sample_standardized = None
    elif sample_type == 'storytelling':
        recording.voice_sample_storytelling = None
    elif sample_type == 'vocal':
        recording.voice_sample_vocal = None
    else:
        return "Invalid sample type", 400
    
    db.session.commit()
    return redirect(request.referrer or url_for('views.dashboards'))

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

@views.route('/admin/export/patient/<int:patient_id>')
@login_required
@admin_required
def export_patient_ai_data(patient_id):
    """Export single patient data with audio files as ZIP for AI development"""
    data = export_patient_data_for_ai(patient_id)
    if not data:
        flash('Patient not found or has no recordings.')
        return redirect(url_for('views.dashboards'))
    
    # Create ZIP in memory
    import io
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add JSON metadata
        json_data = json.dumps(data, indent=2, ensure_ascii=False)
        zipf.writestr(f'patient_{patient_id}_metadata.json', json_data)
        
        # Add audio files
        recordings = Recording.query.filter_by(patient_id=patient_id).all()
        for recording in recordings:
            audio_key = f"{recording.recording_type}_day_{recording.hospitalization_day}"
            
            if recording.voice_sample_standardized:
                format_ext = detect_audio_format(recording.voice_sample_standardized)
                filename = f"audio/patient_{patient_id}_{audio_key}_standardized.{format_ext}"
                zipf.writestr(filename, recording.voice_sample_standardized)
            
            if recording.voice_sample_storytelling:
                format_ext = detect_audio_format(recording.voice_sample_storytelling)
                filename = f"audio/patient_{patient_id}_{audio_key}_storytelling.{format_ext}"
                zipf.writestr(filename, recording.voice_sample_storytelling)
            
            if recording.voice_sample_vocal:
                format_ext = detect_audio_format(recording.voice_sample_vocal)
                filename = f"audio/patient_{patient_id}_{audio_key}_vocal.{format_ext}"
                zipf.writestr(filename, recording.voice_sample_vocal)
        
        # Add README for AI developers
        readme_content = f"""# Patient {patient_id} - AI Development Dataset

## Structure
- `patient_{patient_id}_metadata.json`: Complete patient data in structured format
- `audio/`: Raw audio files organized by recording type and day

## Audio File Naming Convention
- Format: `patient_{{id}}_{{type}}_day_{{day}}_{{sample_type}}.{{extension}}`
- Types: admission, daily, discharge
- Sample types: standardized, storytelling, vocal

## Metadata Structure
- `admission_data`: Demographics, clinical data, lab values, KCCQ scores
- `daily_data`: Daily vitals, medication changes, lab values (array of days)
- `discharge_data`: Discharge information, final lab values, KCCQ scores
- `audio_files`: Metadata about available audio files

## KCCQ Score Categories
- Physical Limitation (kccq1a-1f)
- Symptom Stability (kccq2)
- Symptom Frequency (kccq3-8)
- Symptom Burden (kccq9-12)
- Self Efficacy (kccq13-14)
- Quality of Life (kccq15a-15d)
- Social Limitation (kccq16)

## Export Information
- Export Date: {datetime.datetime.now().isoformat()}
- Total Recordings: {data['metadata']['total_recordings']}
- Hospitalization Days: {data['metadata']['hospitalization_days']}
"""
        zipf.writestr('README.md', readme_content)
    
    zip_buffer.seek(0)
    
    return Response(
        zip_buffer.getvalue(),
        mimetype='application/zip',
        headers={
            'Content-Disposition': f'attachment; filename=patient_{patient_id}_ai_dataset.zip'
        }
    )

@views.route('/admin/export/all_patients')
@login_required
@admin_required
def export_all_patients_ai_data():
    """Export all patients data with audio files as ZIP for AI development"""
    patients = Patient.query.all()
    
    if not patients:
        flash('No patients found.')
        return redirect(url_for('views.dashboards'))
    
    # Create ZIP in memory
    import io
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        all_patients_data = {
            'export_timestamp': datetime.datetime.now().isoformat(),
            'total_patients': len(patients),
            'patients': {}
        }
        
        total_audio_files = 0
        
        for patient in patients:
            patient_data = export_patient_data_for_ai(patient.id)
            if patient_data:
                all_patients_data['patients'][str(patient.id)] = patient_data
                
                # Add audio files for this patient
                recordings = Recording.query.filter_by(patient_id=patient.id).all()
                for recording in recordings:
                    audio_key = f"{recording.recording_type}_day_{recording.hospitalization_day}"
                    
                    if recording.voice_sample_standardized:
                        format_ext = detect_audio_format(recording.voice_sample_standardized)
                        filename = f"audio/patient_{patient.id}/{audio_key}_standardized.{format_ext}"
                        zipf.writestr(filename, recording.voice_sample_standardized)
                        total_audio_files += 1
                    
                    if recording.voice_sample_storytelling:
                        format_ext = detect_audio_format(recording.voice_sample_storytelling)
                        filename = f"audio/patient_{patient.id}/{audio_key}_storytelling.{format_ext}"
                        zipf.writestr(filename, recording.voice_sample_storytelling)
                        total_audio_files += 1
                    
                    if recording.voice_sample_vocal:
                        format_ext = detect_audio_format(recording.voice_sample_vocal)
                        filename = f"audio/patient_{patient.id}/{audio_key}_vocal.{format_ext}"
                        zipf.writestr(filename, recording.voice_sample_vocal)
                        total_audio_files += 1
        
        # Add master JSON metadata
        json_data = json.dumps(all_patients_data, indent=2, ensure_ascii=False)
        zipf.writestr('all_patients_metadata.json', json_data)
        
        # Add comprehensive README
        readme_content = f"""# Complete AI Development Dataset - All Patients

## Overview
This dataset contains complete medical and voice data from {len(patients)} patients for AI/ML development.

## Structure
- `all_patients_metadata.json`: Master metadata file with all patient data
- `audio/patient_{{id}}/`: Audio files organized by patient ID
- Each patient folder contains audio files named: `{{type}}_day_{{day}}_{{sample_type}}.{{extension}}`

## Dataset Statistics
- Total Patients: {len(patients)}
- Total Audio Files: {total_audio_files}
- Export Date: {datetime.datetime.now().isoformat()}

## File Formats
Audio files are stored in their original format (WebM, OGG, MP3, WAV, M4A).

## Data Privacy
This dataset is for authorized AI development only. Ensure compliance with data protection regulations.

## Usage Guidelines
1. Load `all_patients_metadata.json` for structured data access
2. Audio files can be loaded using standard audio processing libraries
3. KCCQ scores are organized by clinical categories for easy analysis
4. Longitudinal data is available through daily recordings

## Contact
For questions about this dataset, contact the system administrator.
"""
        zipf.writestr('README.md', readme_content)
    
    zip_buffer.seek(0)
    
    return Response(
        zip_buffer.getvalue(),
        mimetype='application/zip',
        headers={
            'Content-Disposition': f'attachment; filename=all_patients_ai_dataset_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
        }
    )

@views.route('/admin/export/csv/<int:patient_id>')
@login_required
@admin_required
def export_patient_csv(patient_id):
    """Export patient data as CSV (without audio files) for quick analysis"""
    recordings = Recording.query.filter_by(patient_id=patient_id).order_by(Recording.hospitalization_day).all()
    
    if not recordings:
        flash('Patient not found or has no recordings.')
        return redirect(url_for('views.dashboards'))
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # CSV Headers
    headers = [
        'patient_id', 'recording_id', 'recording_type', 'hospitalization_day', 'date',
        'age', 'gender', 'height', 'diagnosis', 'medication', 'comorbidities',
        'weight', 'current_weight', 'initial_weight', 'bp', 'initial_bp', 'pulse',
        'ntprobnp', 'kalium', 'natrium', 'kreatinin_gfr', 'harnstoff', 'hb',
        'ntprobnp_daily', 'kalium_daily', 'natrium_daily', 'kreatinin_gfr_daily', 
        'harnstoff_daily', 'hb_daily', 'medication_changes',
        'admission_date', 'discharge_date', 'discharge_medication', 'estimated_dryweight', 'abschluss_labor',
        'kccq_total_score', 'kccq1a', 'kccq1b', 'kccq1c', 'kccq1d', 'kccq1e', 'kccq1f',
        'kccq2', 'kccq3', 'kccq4', 'kccq5', 'kccq6', 'kccq7', 'kccq8', 'kccq9',
        'kccq10', 'kccq11', 'kccq12', 'kccq13', 'kccq14', 'kccq15a', 'kccq15b',
        'kccq15c', 'kccq15d', 'kccq16', 'has_audio_standardized', 'has_audio_storytelling', 'has_audio_vocal'
    ]
    writer.writerow(headers)
    
    # Data rows
    for recording in recordings:
        row = [
            recording.patient_id, recording.id, recording.recording_type, 
            recording.hospitalization_day, recording.formatted_calculated_date,
            recording.age, recording.gender, recording.height, recording.diagnosis,
            recording.medication, recording.comorbidities, recording.weight,
            recording.current_weight, recording.initial_weight, recording.bp,
            recording.initial_bp, recording.pulse, recording.ntprobnp,
            recording.kalium, recording.natrium, recording.kreatinin_gfr,
            recording.harnstoff, recording.hb, recording.ntprobnp_daily,
            recording.kalium_daily, recording.natrium_daily, recording.kreatinin_gfr_daily,
            recording.harnstoff_daily, recording.hb_daily, recording.medication_changes,
            recording.admission_date, recording.discharge_date, recording.discharge_medication,
            recording.abschluss_labor, recording.score, recording.kccq1a, recording.kccq1b,
            recording.kccq1c, recording.kccq1d, recording.kccq1e, recording.kccq1f,
            recording.kccq2, recording.kccq3, recording.kccq4, recording.kccq5,
            recording.kccq6, recording.kccq7, recording.kccq8, recording.kccq9,
            recording.kccq10, recording.kccq11, recording.kccq12, recording.kccq13,
            recording.kccq14, recording.kccq15a, recording.kccq15b, recording.kccq15c,
            recording.kccq15d, recording.kccq16,
            recording.voice_sample_standardized is not None,
            recording.voice_sample_storytelling is not None,
            recording.voice_sample_vocal is not None
        ]
        writer.writerow(row)
    
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=patient_{patient_id}_data.csv'}
    )