import torch
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image

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

def are_duplicates(image1_path:str, image2_path:str)->bool:
    """
    image1: path to first image
    image2: path to second image

    Compare two images and return True if they are duplicates
    False otherwise
    """
    image1,image2  = Image.open(image1_path), Image.open(image2_path)
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

if __name__ == '__main__':
    # Load two example images
    img1_path = 'image1.png'
    img2_path = 'image2.jpg'

    print(are_duplicates(img1_path, img2_path))