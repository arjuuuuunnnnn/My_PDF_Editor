import os
from flask import Flask, request, redirect, url_for, session, make_response, render_template
from werkzeug.utils import secure_filename
from flask_cors import CORS
import logging
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('PDF_TO_HTML')

UPLOAD_FOLDER = 'upload'
PDF_TO_HTML_FOLDER = 'pdf2html'

app = Flask(__name__)
ALLOWED_EXTENSIONS = {'pdf', 'PDF'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

CORS(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert2html(file):
    filename = os.path.basename(file)
    html_output_path = os.path.join(PDF_TO_HTML_FOLDER, f"{filename}.html")
    command = f'./pdf2htmlEX-0.18.8.rc1-master-20200630-Ubuntu-bionic-x86_64.AppImage {file} {html_output_path}'

    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, err = process.communicate()
        
        if process.returncode != 0:
            raise Exception(f"Conversion failed with error: {err.decode('utf-8')}")
        
        with open(html_output_path, 'r') as f:
            html_content = f.read()

        return html_content

    except Exception as e:
        logger.error(f"Error in convert2html function: {e}")
        return None

@app.route('/')
def home_page():
    return render_template("index.html")

@app.route('/upload', methods=['POST'])
def fileUpload():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        destination = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(destination)

        html_content = convert2html(destination)
        if html_content:
            return make_response(html_content)
        else:
            return make_response("Error converting PDF to HTML", 500)
    else:
        return redirect(request.url)

if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    if not os.path.exists(PDF_TO_HTML_FOLDER):
        os.makedirs(PDF_TO_HTML_FOLDER)

    app.secret_key = os.urandom(24)
    app.run(debug=True)

