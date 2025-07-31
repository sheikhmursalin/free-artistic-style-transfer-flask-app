import os
import uuid
import threading
import time
from datetime import datetime, timedelta
from flask import Flask, request, render_template, jsonify, send_file, url_for
from werkzeug.utils import secure_filename
from models.style_models import StyleTransfer
from utils.file_utils import allowed_file, cleanup_old_files
from utils.video_utils import process_video_frames
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Create necessary directories
os.makedirs('static/uploads', exist_ok=True)
os.makedirs('static/results', exist_ok=True)

# Initialize style transfer
style_transfer = StyleTransfer()

# Available styles
AVAILABLE_STYLES = {
    'ghibli': 'Studio Ghibli Style',
    'cartoon': 'Cartoon Style',
    'sketch': 'Pencil Sketch',
    'oil_painting': 'Oil Painting',
    'watercolor': 'Watercolor',
    'anime': 'Anime Style'
}

@app.route('/')
def index():
    return render_template('index.html', styles=AVAILABLE_STYLES)

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        style = request.form.get('style', 'cartoon')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        if style not in AVAILABLE_STYLES:
            return jsonify({'error': 'Invalid style selected'}), 400
        
        # Generate unique filename
        unique_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{unique_id}.{file_ext}"
        
        # Save uploaded file
        upload_path = os.path.join('static/uploads', unique_filename)
        file.save(upload_path)
        
        # Process file based on type
        if file_ext in ['mp4', 'avi', 'mov', 'mkv']:
            # Video processing
            result_path = process_video_style_transfer(upload_path, style, unique_id)
        else:
            # Image processing
            result_path = process_image_style_transfer(upload_path, style, unique_id)
        
        # Clean up upload file
        os.remove(upload_path)
        
        return jsonify({
            'success': True,
            'result_url': url_for('static', filename=f'results/{os.path.basename(result_path)}'),
            'download_url': url_for('download_result', filename=os.path.basename(result_path))
        })
    
    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}")
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

def process_image_style_transfer(input_path, style, unique_id):
    """Process single image with style transfer"""
    file_ext = input_path.rsplit('.', 1)[1].lower()
    result_filename = f"{unique_id}_styled.{file_ext}"
    result_path = os.path.join('static/results', result_filename)
    
    # Apply style transfer
    style_transfer.apply_style(input_path, result_path, style)
    
    return result_path

def process_video_style_transfer(input_path, style, unique_id):
    """Process video with style transfer frame by frame"""
    result_filename = f"{unique_id}_styled.mp4"
    result_path = os.path.join('static/results', result_filename)
    
    # Process video frames
    process_video_frames(input_path, result_path, style, style_transfer)
    
    return result_path

@app.route('/download/<filename>')
def download_result(filename):
    try:
        return send_file(os.path.join('static/results', filename), as_attachment=True)
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404

@app.route('/cleanup')
def manual_cleanup():
    """Manual cleanup endpoint for maintenance"""
    cleanup_old_files('static/uploads', hours=1)
    cleanup_old_files('static/results', hours=24)
    return jsonify({'message': 'Cleanup completed'})

# Background cleanup task
def background_cleanup():
    """Background task to clean up old files"""
    while True:
        time.sleep(3600)  # Run every hour
        cleanup_old_files('static/uploads', hours=2)
        cleanup_old_files('static/results', hours=48)

# Start background cleanup thread
cleanup_thread = threading.Thread(target=background_cleanup, daemon=True)
cleanup_thread.start()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)