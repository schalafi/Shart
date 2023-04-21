import io
import random 

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

app = Flask(__name__)
app.config['SECRET_KEY'] = "random string"

def allowed_file_type(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['png', 'jpg', 'jpeg','webp']

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
            print("Uploading : ",filename)
            s3.upload_fileobj(buffer, BUCKET_NAME,filename)
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

