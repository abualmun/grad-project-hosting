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
from torch.utils.data import DataLoader
from torchvision.datasets import ImageFolder

font_path = './fonts/NotoSansArabic-Bold.ttf'
font_manager.fontManager.addfont(font_path)
prop = font_manager.FontProperties(fname=font_path)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class_names = ["الحرم المكي","العلا", "المسجد النبوي",  "جبل أحد", "برج المملكة"]

test_dir = "./locations"  # Root directory containing class folders
model_path = "five_classes_model.pth"

# Define the transform for the input images
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def load_model(model_path, num_classes):
    model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
    model.fc = nn.Linear(in_features=model.fc.in_features, out_features=num_classes)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model = model.to(device)
    model.eval()
    return model

# Load the model
num_classes = len(class_names)
model = load_model(model_path, num_classes)

# Create dataset and dataloader
test_dataset = ImageFolder(root=test_dir, transform=transform)
test_loader = DataLoader(test_dataset, batch_size=1, shuffle=False)

# Collect misclassified images
misclassified_results = []

with torch.no_grad():
    for images, labels in test_loader:
        images = images.to(device)
        labels = labels.to(device)
        
        # Get predictions
        outputs = model(images)
        _, predicted = torch.max(outputs, 1)
        
        # Check if prediction is incorrect
        if predicted.item() != labels.item():
            # Get the original image (before transformations)
            original_image_path = test_dataset.imgs[len(misclassified_results)][0]
            original_image = Image.open(original_image_path).convert('RGB')
            
            # Get class names for predicted and true labels
            predicted_class = class_names[predicted.item()]
            true_class = class_names[labels.item()]
            
            misclassified_results.append((
                original_image,
                predicted_class,
                true_class
            ))

if not misclassified_results:
    print("No misclassified images found!")
else:
    # Create a grid only for misclassified images
    num_images = len(misclassified_results)
    num_cols = min(4, num_images)  # Maximum 4 columns
    num_rows = (num_images + num_cols - 1) // num_cols

    plt.figure(figsize=(15, 10))

    for i, (image, predicted_class, true_class) in enumerate(misclassified_results):
        # Reshape and align Arabic text for both predicted and true labels
        predicted_text = arabic_reshaper.reshape(f"التصنيف: {predicted_class}")
        true_text = arabic_reshaper.reshape(f"الصحيح: {true_class}")
        bidi_predicted = get_display(predicted_text)
        bidi_true = get_display(true_text)

        plt.subplot(num_rows, num_cols, i + 1)
        plt.imshow(image)
        plt.title(f"{bidi_predicted}\n{bidi_true}", fontsize=10, fontproperties=prop)
        plt.axis("off")

    plt.tight_layout()
    plt.show()

# Print overall accuracy
total_images = len(test_loader.dataset)
num_misclassified = len(misclassified_results)
accuracy = (total_images - num_misclassified) / total_images * 100

print(f"\nTest Results:")
print(f"Total images: {total_images}")
print(f"Misclassified images: {num_misclassified}")
print(f"Accuracy: {accuracy:.2f}%")