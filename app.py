import os
from flask import Flask, render_template, request, jsonify, send_from_directory, url_for
from werkzeug.utils import secure_filename
from steganography import hide_message, extract_message

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # Batas ukuran file 2 MB
app.config['UPLOAD_EXTENSIONS'] = ['.m4a', '.mp3', '.wav']
app.config['UPLOAD_INPUT_PATH'] = 'uploads/inputs'
app.config['UPLOAD_OUTPUT_PATH'] = 'uploads/outputs'

# Pastikan direktori upload ada
os.makedirs(app.config['UPLOAD_INPUT_PATH'], exist_ok=True)
os.makedirs(app.config['UPLOAD_OUTPUT_PATH'], exist_ok=True)

@app.errorhandler(413)
def too_large():
    "File terlalu besar", 413

@app.route('/')
def index():
    files = os.listdir(app.config['UPLOAD_INPUT_PATH'])
    return render_template('index.html', files=files)

@app.route('/embed', methods=['GET', 'POST'])
def embed():
    # Periksa apakah file adalah bagian dari permintaan
    if request.method == 'POST':
        if 'file' not in request.files:
            jsonify({"error": "Tidak ada file yang diunggah"}), 400

        uploaded_file = request.files['file']
        filename = secure_filename(uploaded_file.filename)

        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext.lower() not in app.config['UPLOAD_EXTENSIONS']:
                return jsonify({"error": "Format audio tidak valid"}), 400

            # Simpan file yang diunggah
            uploaded_file.save(os.path.join(app.config['UPLOAD_INPUT_PATH'], filename))

            # Ambil pesan yang akan disisipkan dari input field dengan id="input"
            message = request.form.get('input').strip()  # Gunakan 'input' sebagai kunci

            # Validasi pesan untuk memastikan tidak kosong
            if not message:
                return jsonify({"error": "Pesan tidak boleh kosong"}), 400

            # Tentukan jalur input dan output untuk penyisipan
            input_path = os.path.join(app.config['UPLOAD_INPUT_PATH'], filename)
            output_filename = 'output.wav'
            output_path = os.path.join(app.config['UPLOAD_OUTPUT_PATH'], output_filename)

            # Sisipkan pesan ke dalam file WAV
            hide_message(input_path, output_path, message)

            return jsonify({
                "info-message": "Pesan berhasil disisipkan",
                "download_link": url_for('upload', filename=output_filename)
            }), 200

    return jsonify({"error": "Metode permintaan tidak valid"}), 405  # Metode Tidak Diizinkan untuk permintaan GET

@app.route('/extract', methods=['POST'])
def extract():
    # Periksa apakah file adalah bagian dari permintaan
    if 'file' not in request.files:
        return jsonify({"error": "Tidak ada file yang diunggah"}), 400

    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)

    if filename != '':
        output_path = os.path.join(app.config['UPLOAD_INPUT_PATH'], filename)

        # Simpan file yang diunggah untuk ekstraksi
        uploaded_file.save(output_path)

        length = request.form.get('length', 500)  # Panjang default
        result = extract_message(output_path, length)

        return jsonify({
            "message": result
        }), 200

    return jsonify({"error": "Tidak ada file yang diunggah"}), 400

@app.route('/uploads/<filename>')
def upload(filename):
    return send_from_directory(app.config['UPLOAD_OUTPUT_PATH'], filename)

if __name__ == '__main__':
    app.run(debug=True)