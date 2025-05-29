from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
import os
import subprocess
import uuid
from werkzeug.utils import secure_filename
import threading

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB limit

# Store active processes
active_processes = {}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['pdf', 'doc', 'docx']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'pdf_file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    pdf_file = request.files['pdf_file']
    if pdf_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if pdf_file and allowed_file(pdf_file.filename):
        # Generate unique filename
        filename = str(uuid.uuid4()) + '_' + secure_filename(pdf_file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        pdf_file.save(path)
        
        # Store file info in session
        session_id = str(uuid.uuid4())
        file_info = {
            'path': path,
            'filename': pdf_file.filename,
            'session_id': session_id,
            'file_type': pdf_file.content_type
        }
        
        # Start gesture zoom process only for PDF files
        if pdf_file.filename.lower().endswith('.pdf'):
            process = subprocess.Popen(['python', 'gesture_zoom.py', path])
            active_processes[session_id] = process
        
        return jsonify({
            'message': 'File uploaded successfully',
            'session_id': session_id,
            'filename': pdf_file.filename,
            'file_url': f'/static/uploads/{filename}',
            'file_type': pdf_file.content_type
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/terminate/<session_id>')
def terminate_session(session_id):
    if session_id in active_processes:
        active_processes[session_id].terminate()
        del active_processes[session_id]
        return jsonify({'message': 'Session terminated'})
    return jsonify({'error': 'Session not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5001)