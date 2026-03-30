from flask import Flask, render_template, request, redirect, url_for, session, send_file
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader

import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import os
from PIL import Image

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session usage

model = load_model('models/leaf_disease_model.h5')
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Class labels
classes = ['Northern_Leaf_Blight', 'Common_Rust', 'Gray_Leaf_Spot', 'Healthy']


# NPK validation
def validate_npk(n, p, k):
    valid = []
    if 60 <= n <= 80:
        valid.append("N is OK")
    else:
        valid.append("N is OUT OF RANGE")
    if 30 <= p <= 50:
        valid.append("P is OK")
    else:
        valid.append("P is OUT OF RANGE")
    if 40 <= k <= 60:
        valid.append("K is OK")
    else:
        valid.append("K is OUT OF RANGE")
    return ', '.join(valid)


# Image preprocessing
def prepare_image(img_path):
    img = Image.open(img_path).resize((224, 224))
    img_array = image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array


@app.route('/')
def index():
    return render_template('index.html',
                           result=session.pop('result', None),
                           npk_result=session.pop('npk_result', None),
                           image_file=session.pop('image_file', None),
                           show_download=session.pop('show_download', False))


@app.route('/predict', methods=['POST'])
def predict():
    nitrogen = int(request.form['nitrogen'])
    phosphorus = int(request.form['phosphorus'])
    potassium = int(request.form['potassium'])
    npk_result = validate_npk(nitrogen, phosphorus, potassium)

    img_file = request.files['image']
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], img_file.filename)
    img_file.save(img_path)

    img_data = prepare_image(img_path)
    prediction = model.predict(img_data)
    predicted_class = classes[np.argmax(prediction)]

    # Save in session
    session['result'] = predicted_class
    session['npk_result'] = npk_result
    session['image_file'] = img_file.filename
    session['show_download'] = True

    return redirect(url_for('index'))


@app.route('/download_pdf')
def download_pdf():
    result = request.args.get('result')
    npk_result = request.args.get('npk_result')
    image_file = request.args.get('image_file')

    pdf_path = r"C:\Users\nalla\Downloads\result_report.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Maize Leaf Disease Prediction Report")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 100, f"Prediction: {result}")
    c.drawString(50, height - 130, "NPK Validation:")
    text_obj = c.beginText(70, height - 150)
    for line in npk_result.split('\n'):
        text_obj.textLine(line.strip())
    c.drawText(text_obj)

    if image_file:
        image_path = os.path.join('static', 'uploads', image_file)
        if os.path.exists(image_path):
            c.drawImage(ImageReader(image_path), 50, 250, width=200, preserveAspectRatio=True, mask='auto')

    c.save()
    return send_file(pdf_path, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)

# from flask import Flask, render_template, request

# from flask import send_file
# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import letter
# from reportlab.lib.utils import ImageReader

# import numpy as np
# from tensorflow.keras.models import load_model
# from tensorflow.keras.preprocessing import image
# import os
# from PIL import Image

# app = Flask(__name__)
# model = load_model('models/leaf_disease_model.h5')
# UPLOAD_FOLDER = 'static/uploads'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# # Class labels
# classes = ['Northern_Leaf_Blight','Common_Rust', 'Gray_Leaf_Spot', 'Healthy' ]

# # Validate NPK values
# def validate_npk(n, p, k):
#     valid = []
#     if 60 <= n <= 80:
#         valid.append("N is OK")
#     else:
#         valid.append("N is OUT OF RANGE")
#     if 30 <= p <= 50:
#         valid.append("P is OK")
#     else:
#         valid.append("P is OUT OF RANGE")
#     if 40 <= k <= 60:
#         valid.append("K is OK")
#     else:
#         valid.append("K is OUT OF RANGE")
#     return ', '.join(valid)

# # Image preprocessing
# def prepare_image(img_path):
#     img = Image.open(img_path).resize((224, 224))
#     img_array = image.img_to_array(img) / 255.0
#     img_array = np.expand_dims(img_array, axis=0)
#     return img_array

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/predict', methods=['POST'])
# def predict():
#     nitrogen = int(request.form['nitrogen'])
#     phosphorus = int(request.form['phosphorus'])
#     potassium = int(request.form['potassium'])
#     npk_result = validate_npk(nitrogen, phosphorus, potassium)

#     img_file = request.files['image']
#     img_path = os.path.join(app.config['UPLOAD_FOLDER'], img_file.filename)
#     img_file.save(img_path)

#     img_data = prepare_image(img_path)
#     prediction = model.predict(img_data)
#     predicted_class = classes[np.argmax(prediction)]

#     return render_template('index.html',result=predicted_class,npk_result=npk_result,image_file=img_file.filename, show_download=True)

# if __name__ == '__main__':
#     app.run(debug=True)

# # Download option

# @app.route('/download_pdf')
# def download_pdf():
#     result = request.args.get('result')
#     npk_result = request.args.get('npk_result')
#     image_file = request.args.get('image_file')

#     pdf_path = "static/result_report.pdf"
#     c = canvas.Canvas(pdf_path, pagesize=letter)
#     width, height = letter

#     c.setFont("Helvetica-Bold", 16)
#     c.drawString(50, height - 50, "Maize Leaf Disease Prediction Report")

#     c.setFont("Helvetica", 12)
#     c.drawString(50, height - 100, f"Prediction: {result}")
#     c.drawString(50, height - 130, "NPK Validation:")
#     text_obj = c.beginText(70, height - 150)
#     for line in npk_result.split('\n'):
#         text_obj.textLine(line.strip())
#     c.drawText(text_obj)

#     # Add image
#     if image_file:
#         image_path = os.path.join('static', 'uploads', image_file)
#         if os.path.exists(image_path):
#             c.drawImage(ImageReader(image_path), 50, 250, width=200, preserveAspectRatio=True, mask='auto')

#     c.save()

#     return send_file(pdf_path, as_attachment=True)

# # from flask import Flask, request, render_template
# # from model import predict_disease
# # import os

# # # Create a temporary directory if it doesn't exist
# # if not os.path.exists('temp'):
# #     os.makedirs('temp')
# # app = Flask(__name__)

# # @app.route('/')
# # def home():
# #     return render_template('index.html')

# # @app.route('/predict', methods=['POST'])
# # def predict():
# #     if 'file' not in request.files:
# #         return "No file part"
# #     file = request.files['file']
# #     if file.filename == '':
# #         return "No selected file"
# #     prediction = predict_disease(file)
# #     return render_template('result.html', prediction=prediction)

# # if __name__ == '__main__':
# #     app.run(debug=True)

# from flask import Flask, render_template

# app = Flask(__name__)

# @app.route('/')
# def home():
#     return render_template('index.html')

# if __name__ == '__main__':
#     app.run(debug=True)
