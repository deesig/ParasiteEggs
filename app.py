from flask import Flask, request, render_template, jsonify
import os

app = Flask(__name__)

# Ensure there is a folder to save uploaded files
UPLOAD_FOLDER = 'uploads/'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/home')
def renderpage():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    if file and file.filename.endswith(('.png', '.jpg', '.jpeg')):
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        # Process the image through the AI model
        result = process_image(filename)
        return jsonify({'message': f'The AI model processed the image and found {result} items.'})
    else:
        return jsonify({'error': 'Unsupported file type'})

def process_image(image_path):
    # Dummy function for image processing
    # Replace this with actual model prediction code
    return 5  # Assuming the model found 5 items

if __name__ == '__main__':
    app.run(debug=True)
