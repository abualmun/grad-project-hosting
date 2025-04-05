from flask import Flask, request, jsonify
import torch
import torchvision.transforms as transforms
from torchvision import models
import torch.nn as nn
from PIL import Image
import base64
import io
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Class names
class_names = [
    "الحرم المكي",              
    "العلا",                    
    "برج مياه الخبر",          
    "مسجد قباء",               
    "مسجد الراجحي",            
    "المتحف الوطني",
    "المسجد النبوي",            
    "جبل أحد",                  
    "برج المملكة",              
    "المصمك",                   
    "برج الفيصلية",             
    "وادي حنيفة",               
    "فقيه أكواريوم",            
    "كورنيش جدة"            
               
]

# Class descriptions for tourists
class_descriptions = {
    "الحرم المكي": "The Grand Mosque (Al-Haram Mosque) in Mecca is the holiest site in Islam. It surrounds the Kaaba, the building Muslims face during prayer. Millions visit annually for Hajj and Umrah pilgrimages.",
    "العلا": "AlUla is a stunning ancient city featuring Hegra (Madain Saleh), Saudi Arabia's first UNESCO World Heritage site with well-preserved Nabataean tombs carved into sandstone mountains.",
    "برج مياه الخبر": "Khobar Water Tower is a distinctive landmark in the Eastern Province, offering panoramic views of the Arabian Gulf. Its unique design makes it an iconic symbol of the city.",
    "مسجد قباء": "Quba Mosque in Medina is the oldest mosque in the world, established by Prophet Muhammad. Muslims believe praying here earns rewards equivalent to performing an Umrah.",
    "مسجد الراجحي": "Al-Rajhi Mosque in Riyadh is one of the largest mosques in Saudi Arabia, known for its stunning architecture that blends traditional Islamic design with modern elements.",
    "المتحف الوطني": "The National Museum in Riyadh showcases Saudi Arabia's rich heritage through artifacts, interactive displays, and multimedia presentations covering the Arabian Peninsula's history.",
    "المسجد النبوي": "The Prophet's Mosque in Medina is Islam's second holiest site, housing the tomb of Prophet Muhammad. Its distinctive green dome and expansive courtyards welcome millions of pilgrims yearly.",
    "جبل أحد": "Mount Uhud in Medina is historically significant as the site of the Battle of Uhud in 625 CE. It offers panoramic views and holds deep spiritual meaning for Muslims.",
    "برج المملكة": "Kingdom Centre Tower in Riyadh is one of Saudi Arabia's most iconic skyscrapers, featuring a distinctive keyhole design. The Sky Bridge observation deck offers spectacular city views.",
    "المصمك": "Al Masmak Fortress in Riyadh is a clay and mud-brick fort that played a pivotal role in Saudi Arabia's history. Now a museum, it showcases artifacts from the kingdom's unification.",
    "برج الفيصلية": "Al Faisaliyah Tower in Riyadh was the first skyscraper in Saudi Arabia. Its distinctive design culminates in a glass globe housing a restaurant with panoramic city views.",
    "وادي حنيفة": "Wadi Hanifah is a valley that runs through Riyadh, transformed from a waste dump into an environmental rehabilitation project with parks, walking paths, and recreational areas.",
    "فقيه أكواريوم": "Fakieh Aquarium in Jeddah is the first public aquarium in Saudi Arabia, housing over 200 species of marine life. It offers visitors educational and interactive experiences about sea life.",
    "كورنيش جدة": "Jeddah Corniche is a 30km coastal resort area with recreational activities, pavilions, and public art including the famous open-air sculpture museum featuring works by international artists."
 }

# Define the transform for input images
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Load the model
def load_model(model_path, num_classes):
    model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
    model.fc = nn.Linear(in_features=model.fc.in_features, out_features=num_classes)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model = model.to(device)
    model.eval()
    return model

# Function to predict from base64 image
def predict_image_base64(base64_string, model, transform):
    try:
        # Decode base64 image
        image_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        
        # Transform and predict
        image_tensor = transform(image).unsqueeze(0).to(device)
        
        with torch.no_grad():
            output = model(image_tensor)
            probabilities = torch.nn.functional.softmax(output, dim=1)[0]
            _, predicted = torch.max(output, 1)
            predicted_class_index = predicted.item()
            predicted_class = class_names[predicted_class_index]
            confidence = probabilities[predicted_class_index].item() * 100
            
        return {
            "success": True,
            "class": predicted_class,
            "class_index": predicted_class_index,
            "confidence": round(confidence, 2),
            "description": class_descriptions[predicted_class]
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# Load model (path will be updated for deployment)
model_path = os.environ.get("MODEL_PATH", "./model.pth")
num_classes = len(class_names)

# We'll load the model when a request comes in to avoid loading during startup
model = None

@app.route('/api/predict', methods=['POST'])
def predict():
    global model
    
    # Load model if not already loaded
    if model is None:
        try:
            model = load_model(model_path, num_classes)
        except Exception as e:
            return jsonify({"success": False, "error": f"Failed to load model: {str(e)}"}), 500
    
    # Get image from request
    if 'image' not in request.json:
        return jsonify({"success": False, "error": "No image provided"}), 400
    
    # Get base64 image (remove data:image/jpeg;base64, prefix if present)
    base64_image = request.json['image']
    if ',' in base64_image:
        base64_image = base64_image.split(',')[1]
    
    # Make prediction
    result = predict_image_base64(base64_image, model, transform)
    return jsonify(result)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "API is running"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)