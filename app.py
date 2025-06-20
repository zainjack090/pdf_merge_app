from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from PyPDF2 import PdfMerger
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey'
UPLOAD_FOLDER = '/tmp'  # Vercel only allows /tmp for writing
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_files():
    if request.method == 'POST':
        files = request.files.getlist('pdf_files')

        if len(files) == 0 or len(files) > 5:
            flash('Please upload between 1 and 5 PDF files.')
            return redirect(request.url)

        merger = PdfMerger()
        file_paths = []

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                file_paths.append(filepath)
                merger.append(filepath)
            else:
                flash('Only PDF files are allowed.')
                return redirect(request.url)

        output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'merged.pdf')
        merger.write(output_path)
        merger.close()

        # No need to remove files manually in /tmp on Vercel

        return send_file(output_path, as_attachment=True)

    return render_template('index.html')

# Vercel expects this name to locate the app object
if __name__ == '__main__':
    app.run(debug=True)
