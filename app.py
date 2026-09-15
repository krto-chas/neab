"""
NEAB Security Assessment Suite - Flask Web Application
Komplett version utan import-fel
"""
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import os
import sys
from pathlib import Path
import yaml
from datetime import datetime
import subprocess
import json

app = Flask(__name__)
app.secret_key = 'neab-secret-key-change-in-production-2025'

# Konfigurera paths
BASE_DIR = Path(__file__).parent
CONFIG_DIR = BASE_DIR / 'config'
OUTPUT_DIR = BASE_DIR / 'data' / 'output'

# Skapa directories
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@app.route('/')
def index():
    """Startsida"""
    return render_template('index.html')


@app.route('/form/step1', methods=['GET', 'POST'])
def form_step1():
    """Steg 1: Organisationsinformation"""
    if request.method == 'POST':
        session['org_namn'] = request.form.get('org_namn', '')
        session['org_typ'] = request.form.get('org_typ', '')
        session['elnat_kunder'] = int(request.form.get('elnat_kunder', 0))
        session['fv_kunder'] = int(request.form.get('fv_kunder', 0))
        session['personal'] = int(request.form.get('personal', 0))
        session['karnverksamhet'] = request.form.get('karnverksamhet', '')
        session['kritiska_anlaggningar'] = int(request.form.get('kritiska_anlaggningar', 10))

        flash('Organisationsinformation sparad!', 'success')
        return redirect(url_for('form_step2'))

    return render_template('form_step1.html')


@app.route('/form/step2', methods=['GET', 'POST'])
def form_step2():
    """Steg 2: Tillgångar"""
    if request.method == 'POST':
        tillgangar = [t for t in request.form.getlist('tillgang[]') if t.strip()]
        kronjuveler = [k for k in request.form.getlist('kronjuvel[]') if k.strip()]

        session['tillgangar'] = tillgangar
        session['kronjuveler'] = kronjuveler

        flash('Tillgångar sparade!', 'success')
        return redirect(url_for('form_step3'))

    return render_template('form_step2.html')


@app.route('/form/step3', methods=['GET', 'POST'])
def form_step3():
    """Steg 3: Regelverk"""
    if request.method == 'POST':
        session['nis2'] = 'nis2' in request.form
        session['gdpr'] = 'gdpr' in request.form
        session['dora'] = 'dora' in request.form
        session['cer'] = 'cer' in request.form

        flash('Regelverk sparade!', 'success')
        return redirect(url_for('form_step4'))

    return render_template('form_step3.html')


@app.route('/form/step4', methods=['GET', 'POST'])
def form_step4():
    """Steg 4: Granska och generera"""
    if request.method == 'POST':
        try:
            # Skapa YAML-konfiguration
            yaml_data = {
                'organisation': {
                    'namn': session.get('org_namn', 'Nordlunda Energi AB'),
                    'typ': session.get('org_typ', 'dso_fv'),
                    'kunder': {
                        'elnat': session.get('elnat_kunder', 85000),
                        'fjarrvärme': session.get('fv_kunder', 12000)
                    },
                    'personal': session.get('personal', 450),
                    'karnverksamhet': session.get('karnverksamhet', 'Energidistribution'),
                    'kritiska_anlaggningar': session.get('kritiska_anlaggningar', 10)
                },
                'regulatoriska_krav': {
                    'nis2': session.get('nis2', True),
                    'gdpr': session.get('gdpr', True),
                    'dora': session.get('dora', False),
                    'cer': session.get('cer', True)
                },
                'tillgangar': session.get('tillgangar', [
                    'SCADA/DCS',
                    'Identitets- och behörighetsplattform',
                    'Elnätsystem'
                ]),
                'kronjuveler': session.get('kronjuveler', [
                    'Kundregister',
                    'Driftsystem'
                ])
            }

            # Spara YAML
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            yaml_filename = f'neab_input_{timestamp}.yaml'
            yaml_path = CONFIG_DIR / yaml_filename

            with open(yaml_path, 'w', encoding='utf-8') as f:
                yaml.dump(yaml_data, f, allow_unicode=True, default_flow_style=False)

            session['yaml_file'] = str(yaml_path)
            session['timestamp'] = timestamp

            flash(f'Konfiguration skapad: {yaml_filename}', 'success')
            return redirect(url_for('run_analysis'))

        except Exception as e:
            flash(f'Fel: {str(e)}', 'danger')
            return redirect(url_for('form_step4'))

    # GET - visa sammanfattning
    data = {
        'org_namn': session.get('org_namn', ''),
        'org_typ': session.get('org_typ', ''),
        'elnat_kunder': session.get('elnat_kunder', 0),
        'fv_kunder': session.get('fv_kunder', 0),
        'personal': session.get('personal', 0),
        'nis2': session.get('nis2', False),
        'gdpr': session.get('gdpr', False),
        'dora': session.get('dora', False),
        'cer': session.get('cer', False),
    }

    return render_template('form_step4.html', data=data)


@app.route('/run-analysis', methods=['GET', 'POST'])
def run_analysis():
    """Kör analysen"""
    yaml_file = session.get('yaml_file')
    timestamp = session.get('timestamp')

    if not yaml_file or not os.path.exists(yaml_file):
        flash('Ingen konfigurationsfil funnen!', 'danger')
        return redirect(url_for('form_step1'))

    if request.method == 'POST':
        try:
            # Kör huvudskriptet
            result = subprocess.run(
                [sys.executable, 'huvudskript_v2.py'],
                cwd=BASE_DIR,
                capture_output=True,
                text=True,
                timeout=300  # 5 minuter timeout
            )

            if result.returncode == 0:
                session['analysis_complete'] = True
                session['output_folder'] = timestamp
                flash('Analys slutförd!', 'success')
                return redirect(url_for('results'))
            else:
                flash(f'Fel vid analys: {result.stderr}', 'danger')
                return redirect(url_for('run_analysis'))

        except subprocess.TimeoutExpired:
            flash('Analysen tog för lång tid (timeout)', 'danger')
        except Exception as e:
            flash(f'Oväntat fel: {str(e)}', 'danger')

        return redirect(url_for('run_analysis'))

    return render_template('run_analysis.html')


@app.route('/results')
def results():
    """Visa tidigare resultat"""
    results_list = []

    if OUTPUT_DIR.exists():
        output_folders = sorted(OUTPUT_DIR.glob('*'), reverse=True)

        for folder in output_folders[:10]:
            if folder.is_dir():
                pdf_files = list(folder.glob('*Ledningsrapport*.pdf'))
                excel_files = list(folder.glob('*Sakerhetsanalys*.xlsx'))
                heatmap_files = list(folder.glob('*Heatmap*.png'))

                if pdf_files or excel_files:
                    results_list.append({
                        'folder': folder.name,
                        'timestamp': folder.name.replace('_', ' '),
                        'pdf': pdf_files[0].name if pdf_files else None,
                        'excel': excel_files[0].name if excel_files else None,
                        'heatmap': heatmap_files[0].name if heatmap_files else None
                    })

    return render_template('results.html', results=results_list)


@app.route('/download/<folder>/<filename>')
def download_file(folder, filename):
    """Ladda ner fil"""
    file_path = OUTPUT_DIR / folder / filename

    if file_path.exists():
        return send_file(file_path, as_attachment=True, download_name=filename)
    else:
        flash('Filen kunde inte hittas', 'danger')
        return redirect(url_for('results'))


@app.route('/clear-session')
def clear_session():
    """Rensa session"""
    session.clear()
    flash('Session rensad', 'info')
    return redirect(url_for('index'))


if __name__ == '__main__':
    print("=" * 60)
    print("NEAB Security Assessment Suite - Web Interface")
    print("=" * 60)
    print(f"URL: http://localhost:5000")
    print(f"Config dir: {CONFIG_DIR}")
    print(f"Output dir: {OUTPUT_DIR}")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)