from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import os
import shutil
import numpy as np
import cv2
from detection_model import predict

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a_random_secret_key_for_session_handling'
app.config['UPLOAD_1'] = 'uploads_chamber1/'
app.config['UPLOAD_2'] = 'uploads_chamber2/'
app.config['ANNOTATED_IMAGES_1'] = 'static/annotated_images_1/'
app.config['ANNOTATED_IMAGES_2'] = 'static/annotated_images_2/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

global chamber_count_1, chamber_1_str, chamber_count_2, chamber_2_str, avg, avg_str, loading_1, loading_2
chamber_count_1 = 0
chamber_1_str = ""
chamber_count_2 = 0
chamber_2_str = ""
avg = 0
avg_str = ""
loading_1 = False
loading_2 = False

os.makedirs(app.config['UPLOAD_1'], exist_ok=True)
os.makedirs(app.config['UPLOAD_2'], exist_ok=True)
os.makedirs(app.config['ANNOTATED_IMAGES_1'], exist_ok=True)
os.makedirs(app.config['ANNOTATED_IMAGES_2'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about_us')
def about_us():
    return render_template('about_us.html')

@app.route('/gallery1')
def gallery1():
    image_folder = os.path.join('static', 'annotated_images_1')
    image_files = [os.path.join(image_folder, file) for file in os.listdir(image_folder) if file.endswith((".png", ".jpg", ".jpeg"))]
    return render_template('gallery1.html', images=image_files)

@app.route('/gallery2')
def gallery2():
    image_folder = os.path.join('static', 'annotated_images_2')
    image_files = [os.path.join(image_folder, file) for file in os.listdir(image_folder) if file.endswith((".png", ".jpg", ".jpeg"))]
    return render_template('gallery2.html', images=image_files)


@app.route('/count_new')
def count_new():
    global chamber_count_1, chamber_1_str, chamber_count_2, chamber_2_str, avg, avg_str
    
    chamber_count_1 = 0
    chamber_count_2 = 0
    avg = 0
    chamber_1_str = ""
    chamber_2_str = ""
    avg_str = ""
    
    clear_uploads(app.config['UPLOAD_1'])
    clear_uploads(app.config['UPLOAD_2'])
    clear_uploads(app.config['ANNOTATED_IMAGES_1'])
    clear_uploads(app.config['ANNOTATED_IMAGES_2'])
    return render_template('count.html', chamber_1_str = chamber_1_str, avg_str = avg_str, chamber_2_str = chamber_2_str)

@app.route('/count')
def count():
    return render_template('count.html', chamber_1_str = chamber_1_str, avg_str = avg_str, chamber_2_str = chamber_2_str)

@app.route('/upload_1', methods=['POST'])
def upload_1():
    files = request.files.getlist("images")
    session['uploaded_files_1'] = []

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_1'], filename)
            file.save(filepath)
            session['uploaded_files_1'].append(filepath)

    return redirect(url_for('process_images_1'))

@app.route('/upload_2', methods=['POST'])
def upload_2():
    files = request.files.getlist("images")
    session['uploaded_files_2'] = []

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_2'], filename)
            file.save(filepath)
            session['uploaded_files_2'].append(filepath)

    return redirect(url_for('process_images_2'))

@app.route('/process_images_1')
def process_images_1():
    global chamber_count_1, chamber_1_str, chamber_count_2, chamber_2_str, avg, avg_str
    final_count = 0;
    image_paths = session.get('uploaded_files_1', [])
    counts = []
    annotated_images = []

    for image_path in image_paths:
        # Process each image and collect results
        result = predict(image_path)
        counts.append(result[0])
        annotated_images.append(result[1])
        # processed_images.append((image_path, result))

    # Keep track of the final count from all the images
    final_count = round(np.sum(counts))
    
    count = 1
    for image in annotated_images:
        image_path = os.path.join('static/annotated_images_1', f'annotated_image_{count}.jpg')
        print(image_path)
        cv2.imwrite(image_path, image)
        count = count + 1
    
    chamber_count_1 = final_count;
    chamber_1_str = f"{chamber_count_1} Eggs Detected!"
    if chamber_count_1 > 0 and chamber_count_2 > 0:
        avg = round((chamber_count_1 + chamber_count_2) / 2)
        avg_str = f"{avg} Eggs Detected!"

    return render_template('count.html', chamber_1_str = chamber_1_str, avg_str = avg_str, chamber_2_str = chamber_2_str)

@app.route('/process_images_2')
def process_images_2():
    global chamber_count_1, chamber_1_str, chamber_count_2, chamber_2_str, avg, avg_str
    final_count = 0;
    image_paths = session.get('uploaded_files_2', [])
    counts = []
    annotated_images = []

    for image_path in image_paths:
        # Process each image and collect results
        result = predict(image_path)
        counts.append(result[0])
        annotated_images.append(result[1])
        # processed_images.append((image_path, result))

    # Keep track of the final count from all the images
    final_count = round(np.sum(counts))
    
    count = 1
    for image in annotated_images:
        image_path = os.path.join('static/annotated_images_2', f'annotated_image_{count}.jpg')
        cv2.imwrite(image_path, image)
        count = count + 1

    
    chamber_count_2 = final_count;
    chamber_2_str = f"{chamber_count_2} Eggs Detected!"
    if chamber_count_1 > 0 and chamber_count_2 > 0:
        avg = round((chamber_count_1 + chamber_count_2) / 2)
        avg_str = f"{avg} Eggs Detected!"

    return render_template('count.html', chamber_1_str = chamber_1_str, avg_str = avg_str, chamber_2_str = chamber_2_str)

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
    aapp.run(host='0.0.0.0', port=80)
