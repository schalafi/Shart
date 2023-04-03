import io
from datetime import datetime
import random
import os
from base64 import b64encode
import datetime as dt

import boto3

from flask import Flask,flash, render_template, request,redirect, url_for,send_file,g
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from wtforms.validators import InputRequired
#from PIL import Image

#from utilities import request_with_file, image_from_response, image_to_byte_array
from json_utils import list_to_json, json_to_list
from utils import get_random_image

s3 = boto3.client('s3')

BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")
IMAGE_DATA_FILE = 'image_names.json'
IMAGES_FOLDER = os.path.join('static', 'media')


DEFAULT_IMAGE=  "amongus.png"


app = Flask(__name__)
app.config['SECRET_KEY'] = "random string"


## COMMETS DB
##app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
##app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
#db = SQLAlchemy(app)


#download_database()
#db.create_all()
#SQL alchemy
#https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/



#ALL_COMMENTS = get_all_comments()
#print("ALL_COMMENTS: ", ALL_COMMENTS)

#simple_comments = 
'''
    <!doctype html>
    <title>Comments</title>
    <h1>Comments</h1>
'''

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

        if filename == '' or  not  allowed_file_type(filename):
            flash('No selected file')
            return redirect(request.url)
        # Upload the file to S3
        try:
            s3.upload_fileobj(file, BUCKET_NAME, file.filename)
            message = 'File uploaded successfully'
        except NoCredentialsError:
            message = 'Credentials not available'

        # Render a response to the user
        return render_template('index.html', message=message)

    


    

    

    
    


    
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

