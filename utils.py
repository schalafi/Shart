def save_to_s3(file_path,object_name = None):
    """
    file_path: str
        path to file to save
    object_name: str
        only filename of from file_path
    """
    if object_name is None:
        path,object_name = os.path.split(file_path)
        
    with open(file_path, "rb") as f:
        s3.upload_fileobj(f, BUCKET_NAME,object_name)



def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True




def get_random_image(new_image, hidden= False):
    """
    new_image: filaneme of new image (no path)
    hidden: bool 
        if hidden folder is used

    return random_image,path_image
        random_image filename of image
        path_image path to file in app
    """
    
    #download json file with image names
    IMAGES_NAMES_FILE = IMAGE_DATA_FILE
    if hidden:
        IMAGES_NAMES_FILE= HIDDEN_IMAGE_DATA_FILE
        
    s3.download_file(BUCKET_NAME, IMAGES_NAMES_FILE, IMAGES_NAMES_FILE)

    print("DOWNLOADING json file at at: ",IMAGES_NAMES_FILE)

    #get images names as list
    names = json_to_list(IMAGES_NAMES_FILE)
    names_set = set(names)

    random_image = DEFAULT_IMAGE
    #Set image path
    path_image =  os.path.join(
            app.config['UPLOAD_FOLDER'],
            DEFAULT_IMAGE )
    if hidden:
        path_image =os.path.join(
            app.config['HIDDEN_UPLOAD_FOLDER'],
            DEFAULT_IMAGE  )
    
    #Return if duplicated image 
    if new_image  in names_set:
        return random_image, path_image

    #At least 1 image 
    if len(names)> 0:
        #random name
        random_image = random.choice(names)
        path_image = os.path.join(app.config['UPLOAD_FOLDER'], random_image)
        if hidden:
            path_image =os.path.join(
            app.config['HIDDEN_UPLOAD_FOLDER'],
            DEFAULT_IMAGE  )

        # download image to media or hidden folder
        # S3 -> media|hidden
        s3.download_file(BUCKET_NAME, random_image, path_image)
        print("DOWNLOADING RANDOM IMAGE to: ", path_image)

    
    #add new image to IMAGE_DATA_FILE
    names.append(new_image)

    #save to json file
    list_to_json(names,IMAGES_NAMES_FILE)
    #print("ADDED NEW_IMAGE",json_to_list(IMAGES_NAMES_FILE)) 

    #update S3 json file
    save_to_s3(file_path= IMAGES_NAMES_FILE,
        object_name=IMAGES_NAMES_FILE)

    return random_image, path_image