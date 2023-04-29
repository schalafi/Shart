import io
import json
import random 
import time

import numpy as np
import os
import boto3
from botocore.exceptions import NoCredentialsError
from flask import Flask,flash, render_template, request,redirect, url_for,send_file,g
from PIL import Image

from duplicate_detection import are_duplicates_imgs
from duplicate_detection import compute_features
from duplicate_detection import download_feature_vectors

s3 = boto3.client('s3')

BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")
IMAGE_DATA_FILE = 'image_names.json'
IMAGES_FOLDER = os.path.join('static', 'media')
DEFAULT_IMAGE=  "amongus.png"
FEATURE_VECTORS_FILE = 'feature_vectors.json'

from PIL import Image

exts = Image.registered_extensions()
supported_extensions = {ex for ex, f in exts.items() if f in Image.OPEN}
print("Supported extensions: ",supported_extensions)

app = Flask(__name__)
app.config['SECRET_KEY'] = "random string"

FEATURE_VECTORS = download_feature_vectors(
    bucket_name=BUCKET_NAME,
    feature_vectors_file=FEATURE_VECTORS_FILE,
    s3=s3)

def allowed_file_type(filename):
    ext ='.'+ filename.rsplit('.', 1)[1].lower()
    print("ext: ",ext)
    return '.' in filename and \
            ext in supported_extensions

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
            print("No file part")
            return redirect(request.url)
        
        # Get the file from the request
        file = request.files['file']
        filename = file.filename

        uploaded_image = Image.open(file)
        #convert to jpg
        uploaded_image = uploaded_image.convert('RGB')
        #in memory file
        buffer = io.BytesIO() 
        uploaded_image.save(buffer,format = "JPEG")
        buffer.seek(0)

        if filename == '' or  not  allowed_file_type(filename):
            flash('No selected file')
            print("No selected file")
            return redirect(request.url)
        
        time0 = time.time()

        #Duplicate detection
        s3_files = s3.list_objects_v2(Bucket=BUCKET_NAME)['Contents']
        for s3_file in s3_files:
            print("Proccessing image: ",s3_file["Key"] )
            if not allowed_file_type(s3_file['Key']):
                continue
            # Download the file from S3
            s3_buffer = io.BytesIO()
            s3.download_fileobj(BUCKET_NAME, s3_file['Key'], s3_buffer)
            #s3_buffer.seek(0)
            existing_image = Image.open(s3_buffer)

            if are_duplicates_imgs(uploaded_image, existing_image):
                print("Duplicates found, image in bucket: {}, uploaded image: {} ".format(s3_file['Key'], filename ))
                time1 = time.time()
                print("Time to detect duplicate: ", time1-time0)
                return redirect(request.url)
        time1 = time.time()
        print("Time to check there is no duplicates: ", time1-time0)
                
        # Upload the file to S3
        try:
            #Change the name of the file and type
            new_image_filename = str(len(s3_files)+1)+".jpg"
            print("Uploading : ",new_image_filename)
            s3.upload_fileobj(buffer, BUCKET_NAME,new_image_filename)
            message = 'File uploaded successfully'
        except NoCredentialsError:
            message = 'Credentials not available'

        image_url = get_random_image()

        return render_template(template_name,
                random_image=image_url,
                a_var = "Success uploading image")
    
    return render_template(template_name,
            random_image="static/media/amongus_3d.jpg",
            a_var = "Not success uploading image")


def get_random_image():
    """
    Get a random image from the S3 bucket
    Return image url
    """
    # Get a list of all objects in the bucket
    objects = s3.list_objects_v2(Bucket=BUCKET_NAME)['Contents']

    # Select a random object from the list
    random_object = random.choice(objects)

    # Get the URL of the random object
    random_object_url = s3.generate_presigned_url('get_object', Params = {'Bucket': BUCKET_NAME,'Key': random_object["Key"]}, ExpiresIn = 3600)
    return random_object_url




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

