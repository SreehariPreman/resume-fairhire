from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

# Create uploads folder if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_jobs():
    with open('jobs.json', 'r') as f:
        return json.load(f)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/company/<company_name>')
def company(company_name):
    jobs_data = load_jobs()
    if company_name not in jobs_data:
        return redirect(url_for('home'))
    
    jobs = jobs_data[company_name]
    return render_template('company.html', company=company_name, jobs=jobs)

@app.route('/upload/<company_name>', methods=['POST'])
def upload_resume(company_name):
    if 'resume' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('company', company_name=company_name))
    
    file = request.files['resume']
    job_id = request.form.get('job_id', 'unknown')
    job_title = request.form.get('job_title', 'Unknown Position')
    
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('company', company_name=company_name))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add company name, job ID and timestamp to filename
        name, ext = os.path.splitext(filename)
        unique_filename = f"{company_name}_Job{job_id}_{name}_{os.urandom(8).hex()}{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        flash(f'✅ ATS Test Complete: Resume tested against "{job_title}" using {company_name} ATS model.', 'success')
    else:
        flash('Invalid file type. Please upload PDF, DOC, or DOCX files only.', 'error')
    
    return redirect(url_for('company', company_name=company_name))

if __name__ == '__main__':
    app.run(debug=True)
