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

def convert_image_to_pdf_a4(image_path):
    a4_width, a4_height = 595, 842  # A4 size in points at 72 DPI
    image = Image.open(image_path)
    image_ratio = image.width / image.height
    a4_ratio = a4_width / a4_height

    # Maintain aspect ratio
    if image_ratio > a4_ratio:
        new_width = a4_width
        new_height = int(a4_width / image_ratio)
    else:
        new_height = a4_height
        new_width = int(a4_height * image_ratio)

    image = image.resize((new_width, new_height), Image.LANCZOS)

    # Create white A4 background
    a4_image = Image.new("RGB", (a4_width, a4_height), (255, 255, 255))
    paste_x = (a4_width - new_width) // 2
    paste_y = (a4_height - new_height) // 2
    a4_image.paste(image, (paste_x, paste_y))

    pdf_path = image_path.rsplit('.', 1)[0] + '_a4.pdf'
    a4_image.save(pdf_path, "PDF", resolution=100.0)
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
                    pdf_path = convert_image_to_pdf_a4(filepath)
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
