from PIL import Image
import json
import io

import torch
import torchvision.models as models
import torchvision.transforms as transforms


THRESHOLD = 1e-9
# Load pre-trained ResNet-50 model
model = models.resnet50(weights='ResNet50_Weights.DEFAULT')

# Remove last layer and freeze weights
model = torch.nn.Sequential(*(list(model.children())[:-1]))
for param in model.parameters():
    param.requires_grad = False

# Define preprocessing transforms
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])


def get_image_with_3_channels(image_path):
    image = Image.open(image_path)
    # Convert image to RGB mode to get 3 channels
    image = image.convert('RGB')
    return image


def compute_features(image:Image):
    """
    image: PIL Image

    Compute features for the image
    """
    # Preprocess image and extract features
    image_tensor = transform(image).unsqueeze(0)
    features = model(image_tensor).detach().numpy().squeeze()
    
    return features

def are_duplicates(image1_path:str, image2_path:str)->bool:
    """
    image1: path to first image
    image2: path to second image

    Compare two images and return True if they are duplicates
    False otherwise
    """
    image1,image2  = get_image_with_3_channels(image1_path), get_image_with_3_channels(image2_path)
    
    # Preprocess images and extract features
    image1_tensor = transform(image1).unsqueeze(0)
    image2_tensor = transform(image2).unsqueeze(0)
    features1 = model(image1_tensor).detach().numpy().squeeze()
    features2 = model(image2_tensor).detach().numpy().squeeze()

    # Compare feature vectors
    distance = torch.dist(torch.tensor(features1), torch.tensor(features2))
    distance = distance.item()
    #print("Distance: ",distance)
    if distance < THRESHOLD:
        #print('Images are duplicates')
        return True
    return False 


def are_duplicates_imgs(image1:Image, image2:Image)->bool:
    """
    image1: path to first image
    image2: path to second image

    Compare two images and return True if they are duplicates
    False otherwise
    """
    print("image1, image2 shapes:", image1.mode, image2.mode)

    #Always convert to a 3 channel image (RGB)
    image1 = image1.convert('RGB')
    image2 = image2.convert('RGB')

    # Preprocess images and extract features
    image1_tensor = transform(image1).unsqueeze(0)
    image2_tensor = transform(image2).unsqueeze(0)
    features1 = model(image1_tensor).detach().numpy().squeeze()
    features2 = model(image2_tensor).detach().numpy().squeeze()

    # Compare feature vectors
    distance = torch.dist(torch.tensor(features1), torch.tensor(features2))
    distance = distance.item()
    print("Distance: ",distance)
    if distance < THRESHOLD:
        #print('Images are duplicates')
        return True
    return False 

def download_feature_vectors(bucket_name:str, feature_vectors_file:str,s3)->dict:
    """
    bucket_name: S3 bucket name
    feature_vectors_file: S3 key for feature vectors file
    s3: boto3 S3 client
    """
    # Load feature vectors file from S3
    try:
        s3.download_file(bucket_name, feature_vectors_file, feature_vectors_file)
        with open(feature_vectors_file, 'r') as f:
            feature_vectors = json.load(f)
    except:
        feature_vectors = {}
    
    return feature_vectors


def store_features(filename:str,image:Image,bucket_name:str,feature_vectors_file:str, feature_vectors:dict,s3):
    """
    filename: name of the image
    image: image to store

    Store the features of the image in the database
    """
    #Compute features
    uploaded_image_features = compute_features(image)
    # Add new feature vector to feature_vectors dict
    feature_vectors[filename] = uploaded_image_features.tolist()
    with open(feature_vectors_file, 'w') as f:
        json.dump(feature_vectors, f)
    
    # Upload updated feature vectors file to S3
    updated_feature_vectors_buffer = io.BytesIO()
    json.dump(feature_vectors, updated_feature_vectors_buffer)
    updated_feature_vectors_buffer.seek(0)
    s3.upload_fileobj(updated_feature_vectors_buffer, bucket_name, feature_vectors_file)

    return uploaded_image_features
    


if __name__ == '__main__':
    # Load two example images
    img1_path ="18.jpg" #'image1.png'
    img2_path ="19.jpg" #'image2.jpg'

    print(are_duplicates(img1_path, img2_path))
    print(are_duplicates_imgs(Image.open(img1_path), Image.open(img2_path)))
    