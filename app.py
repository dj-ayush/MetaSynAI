from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import subprocess
import uuid
from werkzeug.utils import secure_filename
import threading
import signal
import atexit

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB

# Store active subprocesses: {session_id: {'process': Popen, 'thread': Thread}}
active_processes = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['pdf', 'doc', 'docx']

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
        filename = str(uuid.uuid4()) + '_' + secure_filename(pdf_file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        pdf_file.save(path)

        session_id = str(uuid.uuid4())
        file_type = pdf_file.content_type

        if filename.lower().endswith('.pdf'):
            process = subprocess.Popen(
                ['python', 'gesture_zoom.py', path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Thread to monitor process and log output
            def monitor_process(proc, sid):
                try:
                    stdout, stderr = proc.communicate()
                    if stdout:
                        print(f"[{sid}] STDOUT:\n{stdout}")
                    if stderr:
                        print(f"[{sid}] STDERR:\n{stderr}")
                except Exception as e:
                    print(f"[{sid}] Error monitoring process: {e}")
                finally:
                    if sid in active_processes:
                        del active_processes[sid]
                        print(f"[{sid}] Process ended and cleaned up.")

            thread = threading.Thread(target=monitor_process, args=(process, session_id))
            thread.start()

            active_processes[session_id] = {'process': process, 'thread': thread}

        return jsonify({
            'message': 'File uploaded successfully',
            'session_id': session_id,
            'filename': pdf_file.filename,
            'file_url': f'/static/uploads/{filename}',
            'file_type': file_type
        })

    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/terminate/<session_id>')
def terminate_session(session_id):
    if session_id in active_processes:
        process_info = active_processes[session_id]
        process = process_info['process']
        process.terminate()
        process.wait(timeout=5)
        del active_processes[session_id]
        return jsonify({'message': 'Session terminated'})
    return jsonify({'error': 'Session not found'}), 404

# Ensure all subprocesses are terminated on shutdown
def cleanup():
    for sid, process_info in list(active_processes.items()):
        print(f"Cleaning up process {sid}")
        process_info['process'].terminate()
        try:
            process_info['process'].wait(timeout=5)
        except Exception:
            process_info['process'].kill()
        del active_processes[sid]

atexit.register(cleanup)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
