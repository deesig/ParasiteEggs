from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import os
import shutil
import numpy as np
from detection_model import predict

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a_random_secret_key_for_session_handling'
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('hometest.html')

@app.route('/upload_page')
def upload_page():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist("images")
    session['uploaded_files'] = []

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            session['uploaded_files'].append(filepath)

    return redirect(url_for('process_images'))

@app.route('/process_images')
def process_images():
    final_count = 0;
    image_paths = session.get('uploaded_files', [])
    processed_images = []
    processed_messages = []

    for image_path in image_paths:
        # Process each image and collect results
        result = process_image(image_path)
        processed_images.append(result[0])
        processed_messages.append(result[1])
        # processed_images.append((image_path, result))

    # Keep track of the final count from all the images
    final_count = np.sum(processed_images)
    
    # Cleanup uploaded files after processing
    clear_uploads(app.config['UPLOAD_FOLDER'])

    return render_template('results.html', processed_images=processed_messages, final_count = final_count)

def process_image(image_path):
    return (predict(image_path), f"Successfully Processed {image_path}")

def clear_uploads(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

if __name__ == '__main__':
    app.run(debug=True)