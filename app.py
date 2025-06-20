from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from PyPDF2 import PdfMerger
from PIL import Image
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_image_to_pdf(image_path):
    image = Image.open(image_path)
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
    pdf_path = image_path.rsplit('.', 1)[0] + '.pdf'
    image.save(pdf_path, "PDF", resolution=100.0)
    return pdf_path

@app.route('/', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        files = request.files.getlist('files')

        if len(files) == 0 or len(files) > 5:
            flash('Please upload between 1 and 5 files.')
            return redirect(request.url)

        merger = PdfMerger()
        file_paths = []
        temp_pdfs = []

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                ext = filename.rsplit('.', 1)[1].lower()

                if ext == 'pdf':
                    merger.append(filepath)
                    file_paths.append(filepath)
                else:
                    pdf_path = convert_image_to_pdf(filepath)
                    merger.append(pdf_path)
                    file_paths.append(filepath)
                    temp_pdfs.append(pdf_path)
            else:
                flash('Only PDF and image files (png, jpg, jpeg) are allowed.')
                return redirect(request.url)

        output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'merged_output.pdf')
        merger.write(output_path)
        merger.close()

        for path in file_paths + temp_pdfs:
            if os.path.exists(path):
                os.remove(path)

        return send_file(output_path, as_attachment=True)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
