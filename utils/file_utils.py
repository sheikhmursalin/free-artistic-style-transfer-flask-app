import os
import time
from datetime import datetime, timedelta

ALLOWED_EXTENSIONS = {
    'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff',  # Images
    'mp4', 'avi', 'mov', 'mkv', 'webm'           # Videos
}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup_old_files(directory, hours=24):
    """Remove files older than specified hours"""
    if not os.path.exists(directory):
        return
    
    cutoff_time = time.time() - (hours * 3600)
    
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            if os.path.getctime(file_path) < cutoff_time:
                try:
                    os.remove(file_path)
                    print(f"Removed old file: {filename}")
                except Exception as e:
                    print(f"Error removing {filename}: {e}")

def get_file_size_mb(file_path):
    """Get file size in MB"""
    return os.path.getsize(file_path) / (1024 * 1024)