import torch
import torchvision.transforms as transforms
from torchvision import models
import torch.nn as nn
from PIL import Image
import os
import matplotlib.pyplot as plt
import arabic_reshaper
from bidi.algorithm import get_display
import matplotlib.font_manager as font_manager


font_path = './fonts/NotoSansArabic-Bold.ttf'
font_manager.fontManager.addfont(font_path)
prop = font_manager.FontProperties(fname=font_path)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class_names = ["الحرم المكي"
                ,"العلا"
                ,"المسجد النبوي"
                ,"جبل أحد"
                ,"برج المملكة"
                ,"المصمك" 
                ,"برج الفيصلية"
                ,"وادي حنيفة"
                ,"فقيه أكواريوم"
                ,"كورنيش جدة"
                ,"برج مياه الخبر"
                ,"مسجد قباء"
                ,"مسجد الراجحي" 
                ,"المتحف الوطني" 
                ]  

image_dir = "./test_images"  # Directory containing images to test

model_path = "five_classes_model.pth"  # Path to your saved model


# Define the transform for the input images
transform = transforms.Compose([
    transforms.Resize((224, 224)),  # Resize to match the input size of the model
    transforms.ToTensor(),          # Convert to tensor
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])  # Normalize
])

# Load the trained model
def load_model(model_path, num_classes):
    # Use the new `weights` parameter instead of `pretrained`
    model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
    model.fc = nn.Linear(in_features=model.fc.in_features, out_features=num_classes)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model = model.to(device)
    model.eval()
    return model

# Function to perform inference on a single image
def predict_image(image_path, model, transform):
    image = Image.open(image_path).convert("RGB")  # Open and convert to RGB
    image_tensor = transform(image).unsqueeze(0).to(device)  # Apply transform and add batch dimension

    with torch.no_grad():
        output = model(image_tensor)
        _, predicted = torch.max(output, 1)
        predicted_class = class_names[predicted.item()]

    return image, predicted_class

# Load the model
num_classes = len(class_names)
model = load_model(model_path, num_classes)

# Get list of images in the directory
image_files = [os.path.join(image_dir, f) for f in os.listdir(image_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]

# Create a grid to display images with predictions
num_images = len(image_files)
num_cols = 4  # Number of columns in the grid
num_rows = (num_images + num_cols - 1) // num_cols

plt.figure(figsize=(15, 10))

for i, image_path in enumerate(image_files):
    image, predicted_class = predict_image(image_path, model, transform)

    # Reshape and align Arabic text
    reshaped_text = arabic_reshaper.reshape(f"التصنيف: {predicted_class}")  # Reshape Arabic text
    bidi_text = get_display(reshaped_text)  # Apply bidirectional algorithm

    # Display the image with the predicted class name
    plt.subplot(num_rows, num_cols, i + 1)
    plt.imshow(image)
    plt.title(f"{bidi_text}", fontsize=12, fontproperties=prop)  # Use reshaped and bidi text
    plt.axis("off")

plt.tight_layout()
plt.show() 