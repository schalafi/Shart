import io

import numpy as np
import os
import boto3
from botocore.exceptions import NoCredentialsError
from flask import Flask,flash, render_template, request,redirect, url_for,send_file,g
from PIL import Image


s3 = boto3.client('s3')

BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")
IMAGE_DATA_FILE = 'image_names.json'
IMAGES_FOLDER = os.path.join('static', 'media')
DEFAULT_IMAGE=  "amongus.png"

HISTOGRAMS = {}
def load_histograms():
    # Load histograms of all images in the S3 bucket into memory
    histograms = {}
    for obj in s3.list_objects_v2(Bucket=BUCKET_NAME)['Contents']:
        if obj['Key'].endswith('.npy'):
            response = s3.get_object(Bucket=BUCKET_NAME, Key=obj['Key'])
            histogram = np.load(response['Body'])
            # Add the histogram to the histograms dictionary
            histograms[obj['Key'][:-4]] = histogram  # remove the '.npy' extension from the key
    print("HISTOGRAMS: ", histograms)
    return histograms 
HISTOGRAMS = load_histograms()

app = Flask(__name__)
app.config['SECRET_KEY'] = "random string"

def allowed_file_type(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['png', 'jpg', 'jpeg']

@app.route("/", methods=['POST','GET'])
def index():
    template_name = 'index.html'

    if request.method == 'GET':
        return render_template(template_name,
            random_image="static/media/amongus_3d.jpg",
            a_var = "Waiting to get image.")

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        # Get the file from the request
        file = request.files['file']
        filename = file.filename


        # Create a buffer containing the file contents
        buffer = io.BytesIO()
        file.save(buffer)
        buffer.seek(0)

        if filename == '' or  not  allowed_file_type(filename):
            flash('No selected file')
            return redirect(request.url)
        # Upload the file to S3
        try:
            s3.upload_fileobj(buffer, BUCKET_NAME, file.filename)
            message = 'File uploaded successfully'
        except NoCredentialsError:
            message = 'Credentials not available'
        
         # Compute the histogram of the uploaded image
        image = np.array(Image.open(file.stream))
        print("IMAGE SHAPE: ", image.shape)
        hist, _ = np.histogramdd(np.squeeze(image[:,:,0]).T, bins=(8, 8), range=((0, 256), (0, 256)))
        
        # Save the histogram as a .npy file in the S3 bucket
        histogram_key = f'{file.filename[:-4]}.npy'
        with io.BytesIO() as buffer:
            np.save(buffer, hist)
            buffer.seek(0)
            s3.upload_fileobj(buffer, BUCKET_NAME, histogram_key)

        # Add the histogram to the histograms dictionary
        HISTOGRAMS[file.filename[:-4]] = hist
        # Retrieve a random image from the S3 bucket
        random_key = np.random.choice(list(HISTOGRAMS.keys()))
        response = s3.get_object(Bucket=BUCKET_NAME, Key=random_key)
        image_url = f'https://{BUCKET_NAME}.s3.amazonaws.com/{random_key}'

            
        return render_template(template_name,
                random_image= image_url,
                a_var = "Success uploading image")
    

    
   


    return render_template(template_name,
            random_image="static/media/amongus_3d.jpg",
            a_var = "Not success uploading image")



    


    

    

    
    


    
#TUTORIALES 
#https://hackersandslackers.com/flask-routes/

#File upload
#https://flask.palletsprojects.com/en/2.1.x/patterns/fileuploads/

#sql jinja 
#https://pythonbasics.org/flask-sqlalchemy/


#Basic flask 
#https://flask.palletsprojects.com/en/1.1.x/quickstart/#rendering-templates

#jinja2
#https://www.codecademy.com/learn/learn-flask/modules/flask-templates-and-forms/cheatsheet
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)

