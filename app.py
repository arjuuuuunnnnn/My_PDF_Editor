from flask import Flask, render_template, request, redirect, url_for
from PyPDF2 import PdfReader
from docx import Document
import os

app = Flask(__name__)

UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__))
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
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

if __name__ == '__main__':
    app.run(debug=True)
