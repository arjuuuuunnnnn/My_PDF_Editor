import os
from flask import Flask, flash, request, redirect, url_for, session, make_response, render_template
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
import logging
from celery import Celery
from subprocess import Popen, PIPE
import subprocess
from PyPDF2 import PdfReader
from docx import Document


logging.basicConfig(level=logging.INFO)

logger = logging.getLogger('HELLO WORLD')

BROKER_URL = 'amqp://guest:guest@localhost:5672//'


UPLOAD_FOLDER = 'upload'
PDF_TO_HTML_FOLDER = 'pdf2html'

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'pdf'}
UPLOAD_FOLDER_DOC = os.path.dirname(os.path.abspath(__file__))
app.config['UPLOAD_FOLDER_DOC'] = UPLOAD_FOLDER_DOC

celery = Celery(app.name, broker=BROKER_URL)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@celery.task(bind=True)
def convert2html(self, file):
    print(file)
    filename = file.split('/')[-1]
    command = './pdf2htmlEX-0.18.8.rc1-master-20200630-Ubuntu-bionic-x86_64.AppImage {} ./pdf2html/{}.html'.format(file, filename)
    print ("Executing " + command)
    process = subprocess.Popen(command, stdout = subprocess.PIPE, shell=True)
    output, err = process.communicate()
    
    html_file_location = './' + 'pdf2html' + '/' + filename + ".html"
    f = open(html_file_location)
    s = f.read()
    logger.info("Read the HTML file")

    delete_html_file = 'rm {}{}.html'.format(PDF_TO_HTML_FOLDER, filename)
    delete_uploaded_file = 'rm {}'.format(file)
    #logger.info("Deleted the HTML File")

    #subprocess.Popen(delete_html_file, stdout = subprocess.PIPE, shell=True)
    subprocess.Popen(delete_uploaded_file, stdout = subprocess.PIPE, shell=True)

    return s

@app.route('/')
def home_page():
    return render_template("index.html")

@app.route('/name')
def index():
    return make_response("Backend working !")

@app.route('/upload',methods=['POST'])
def fileUpload():
    target=UPLOAD_FOLDER
    if not os.path.isdir(target):
        os.mkdir(target)
    logger.info("welcome to upload`")
    file = request.files['file']
    filename = secure_filename(file.filename)
    destination="/".join([target, filename])
    file.save(destination)

    pdf2htmltext = convert2html(destination)

    session['uploadFilePath']=destination
    return make_response(pdf2htmltext)


# DOC converter starts
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def pdf_to_text(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PdfReader(file)
        num_pages = len(reader.pages)
        for page_num in range(num_pages):
            page = reader.pages[page_num]
            text += page.extract_text()
    return text

def text_to_word(text, word_path):
    doc = Document()
    doc.add_paragraph(text)
    doc.save(word_path)
    print("Word document created successfully.")

@app.route('/upload_doc', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = file.filename
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(pdf_path)
        text = pdf_to_text(pdf_path)
        word_filename = filename.rsplit('.', 1)[0] + '.docx'
        word_path = os.path.join(app.config['UPLOAD_FOLDER'], word_filename)
        text_to_word(text, word_path)
        return redirect(url_for('index', filename=word_filename))
    else:
        return redirect(request.url)

if __name__ == "__main__":
    app.secret_key = os.urandom(24)
    app.run(debug=True)

flask_cors.CORS(app)

