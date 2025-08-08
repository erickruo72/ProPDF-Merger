import os
from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
import io
from datetime import datetime
import uuid
import shutil
import time

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'temp_uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB limit
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

# Ensure temp directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def cleanup_old_files():
    """Remove files older than 1 hour"""
    now = datetime.now()
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            if (now - file_time).seconds > 3600:  # 1 hour
                if os.path.isfile(filepath):
                    os.unlink(filepath)
                elif os.path.isdir(filepath):
                    shutil.rmtree(filepath)
        except Exception as e:
            print(f"Error deleting file {filepath}: {e}")

def safe_file_operation(filepath, operation, retries=3, delay=0.1):
    """Handle file operations with retries for Windows file locking issues"""
    for i in range(retries):
        try:
            return operation(filepath)
        except PermissionError as e:
            if i == retries - 1:
                raise
            time.sleep(delay)
    return None

@app.route('/')
def index():
    cleanup_old_files()
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files uploaded'}), 400
    
    files = request.files.getlist('files[]')
    upload_details = []
    
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_id = str(uuid.uuid4())
            temp_filename = f"{unique_id}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
            
            try:
                file.save(filepath)
                
                # Get page count
                def read_pdf(p):
                    with open(p, 'rb') as f:
                        return len(PdfReader(f).pages)
                
                page_count = safe_file_operation(filepath, read_pdf)
                if page_count is None:
                    return jsonify({'error': f'Could not read PDF: {filename}'}), 400
                
                upload_details.append({
                    'original_name': filename,
                    'temp_name': temp_filename,
                    'page_count': page_count,
                    'rotation': 0  # Default rotation
                })
            except Exception as e:
                return jsonify({'error': f'Error processing {filename}: {str(e)}'}), 400
    
    return jsonify({'files': upload_details})

@app.route('/preview', methods=['POST'])
def preview_page():
    data = request.json
    temp_filename = data.get('filename')
    rotation = data.get('rotation', 0)
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
    
    try:
        def generate_preview(p):
            with open(p, 'rb') as f:
                reader = PdfReader(f)
                writer = PdfWriter()
                page = reader.pages[0]
                
                if rotation in [90, 180, 270]:
                    page.rotate(rotation)
                
                writer.add_page(page)
                
                buffer = io.BytesIO()
                writer.write(buffer)
                buffer.seek(0)
                return buffer
        
        buffer = safe_file_operation(filepath, generate_preview)
        if buffer is None:
            return jsonify({'error': 'Could not generate preview'}), 500
        
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=False,
            download_name='preview.pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/merge', methods=['POST'])
def merge_pdfs():
    data = request.json
    if not data or 'files' not in data:
        return jsonify({'error': 'No files to merge'}), 400
    
    merger = PdfMerger()
    output_buffer = io.BytesIO()
    files_to_cleanup = []
    
    try:
        for file_info in data['files']:
            temp_filename = file_info['temp_name']
            rotation = file_info.get('rotation', 0)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
            files_to_cleanup.append(filepath)
            
            if rotation in [90, 180, 270]:
                # Need to rotate pages - create temporary rotated version
                def create_rotated(p):
                    with open(p, 'rb') as f:
                        reader = PdfReader(f)
                        writer = PdfWriter()
                        for page in reader.pages:
                            page.rotate(rotation)
                            writer.add_page(page)
                        
                        rotated_buffer = io.BytesIO()
                        writer.write(rotated_buffer)
                        rotated_buffer.seek(0)
                        return rotated_buffer
                
                rotated_buffer = safe_file_operation(filepath, create_rotated)
                if rotated_buffer is None:
                    raise Exception(f"Could not rotate file: {temp_filename}")
                
                merger.append(rotated_buffer)
            else:
                # No rotation needed
                merger.append(filepath)
        
        merger.write(output_buffer)
        output_buffer.seek(0)
        
        return send_file(
            output_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='merged_document.pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        merger.close()
        # Clean up files after sending response
        for filepath in files_to_cleanup:
            try:
                if os.path.exists(filepath):
                    os.unlink(filepath)
            except Exception as e:
                print(f"Error deleting file {filepath}: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)