from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import os
# Import OCR and Translation Libraries
from googletrans import Translator
from PIL import Image
import pytesseract

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/images/'
app.secret_key = 'your_secret_key'  # Required for flashing messages

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
            flash('No text detected in the image. Please try again with another image.')
            return redirect(url_for('index'))
    else:
        flash('No image found. Please upload an image first.')
        return redirect(url_for('index'))

@app.route('/translate')
def translate():
    lang = request.args.get('lang')
    detected_text = request.args.get('detected_text')

    # Translate detected text
    translator = Translator()
    try:
        translated_text = translator.translate(detected_text, dest=lang).text
    except Exception as e:
        translated_text = 'Translation failed: {}'.format(str(e))
    
    return jsonify({'translated_text': translated_text})

if __name__ == '__main__':
    app.run(debug=True)
