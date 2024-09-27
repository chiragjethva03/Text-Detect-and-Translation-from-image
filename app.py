from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import os
# Import OCR and Translation Libraries
from PIL import Image
import pytesseract
import requests

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/images/'
app.secret_key = 'thisistextdetection'  # Required for flashing messages

# API details for translation
RAPIDAPI_KEY = '0fa716fe60mshdbcee860904e14ep1cd9d2jsn4d387ca2dbb3'
RAPIDAPI_HOST = 'free-google-translator.p.rapidapi.com'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'image.png')
    file.save(file_path)
    return redirect(url_for('detect'))

@app.route('/capture')
def capture():
    return render_template('capture.html')

@app.route('/display')
def display():
    return render_template('display.html')

@app.route('/delete', methods=['POST'])
def delete():
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'image.png')
    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({'message': 'Image deleted successfully'}), 200
    else:
        return jsonify({'message': 'No image to delete'}), 404

@app.route('/detect')
def detect():
    # Detect text in the image
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'image.png')
    if os.path.exists(file_path):
        # Use OCR to detect text
        image = Image.open(file_path)
        detected_text = pytesseract.image_to_string(image).strip()
        if detected_text:
            return render_template('translate.html', detected_text=detected_text)
        else:
            flash('No text detected in the image. Please try again with another image.', 'error')
            return redirect(url_for('index'))
    else:
        flash('No image found. Please upload an image first.', 'error')
        return redirect(url_for('index'))

@app.route('/translate', methods=['GET'])
def translate():
    lang = request.args.get('lang')
    detected_text = request.args.get('detected_text')

    if not lang or not detected_text:
        return jsonify({'error': 'Language or detected text not provided'}), 400

    url = f'https://{RAPIDAPI_HOST}/external-api/free-google-translator'
    headers = {
        'content-type': 'application/json',
        'x-rapidapi-host': RAPIDAPI_HOST,
        'x-rapidapi-key': RAPIDAPI_KEY
    }
    payload = {
        'from': 'en',  # Assuming the detected text is in English
        'to': lang,
        'query': detected_text
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        return jsonify({'translated_text': response.json().get('translation')})
    else:
        return jsonify({'error': f'Translation failed with status code {response.status_code}'}), response.status_code


if __name__ == '__main__':
    app.run(debug=True)
