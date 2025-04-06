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
    "الحرم المكي": "الحرم المكي في مكة هو أقدس موقع في الإسلام. يحيط بالكعبة، المبنى الذي يتوجه المسلمون نحوه أثناء الصلاة. يزور الملايين الحرم سنويًا لأداء مناسك الحج والعمرة.",
    "العلا": "العلا هي مدينة تاريخية رائعة تحتوي على مدائن صالح، أول موقع سعودي ضمن قائمة التراث العالمي لليونسكو، وهي مشهورة بالقبور النبطية المنحوتة في الجبال الرملية.",
    "برج مياه الخبر": "برج مياه الخبر هو معلم مميز في المنطقة الشرقية، يوفر إطلالات بانورامية على الخليج العربي. تصميمه الفريد يجعله رمزًا مميزًا للمدينة.",
    "مسجد قباء": "مسجد قباء في المدينة المنورة هو أقدم مسجد في العالم، أسسه النبي محمد صلى الله عليه وسلم. يعتقد المسلمون أن الصلاة هنا تعادل ثواب أداء عمرة.",
    "مسجد الراجحي": "مسجد الراجحي في الرياض هو واحد من أكبر المساجد في السعودية، ويشتهر بتصميمه المعماري الرائع الذي يمزج بين التصميم الإسلامي التقليدي والعناصر الحديثة.",
    "المتحف الوطني": "المتحف الوطني في الرياض يعرض تراث السعودية الغني من خلال القطع الأثرية والعروض التفاعلية والعروض متعددة الوسائط التي تغطي تاريخ شبه الجزيرة العربية.",
    "المسجد النبوي": "المسجد النبوي في المدينة المنورة هو ثاني أقدس موقع في الإسلام، ويضم قبر النبي محمد صلى الله عليه وسلم. قبة المسجد الخضراء وساحاته الواسعة تستقبل الملايين من الزوار سنويًا.",
    "جبل أحد": "جبل أحد في المدينة المنورة له أهمية تاريخية كونه موقع معركة أحد في عام 625م. يوفر إطلالات بانورامية ويحمل معاني روحية عميقة للمسلمين.",
    "برج المملكة": "برج المملكة في الرياض هو واحد من أبرز ناطحات السحاب في السعودية، ويتميز بتصميمه الفريد الذي يشبه المفتاح. توفر منصة السماء إطلالات رائعة على المدينة.",
    "المصمك": "قصر المصمك في الرياض هو قلعة مبنية من الطين والطوب لعبت دورًا محوريًا في تاريخ المملكة العربية السعودية. ويعد الآن متحفًا يعرض قطعًا أثرية من تاريخ توحيد المملكة.",
    "برج الفيصلية": "برج الفيصلية في الرياض هو أول ناطحة سحاب في السعودية. يتميز تصميمه الفريد الذي ينتهي بكرة زجاجية تضم مطعمًا يقدم إطلالات بانورامية على المدينة.",
    "وادي حنيفة": "وادي حنيفة هو وادٍ يمتد عبر الرياض، وقد تم تحويله من مكب نفايات إلى مشروع بيئي يتضمن حدائق ومسارات مشي ومناطق ترفيهية.",
    "فقيه أكواريوم": "أكواريوم فقيه في جدة هو أول أكواريوم عام في السعودية، ويضم أكثر من 200 نوع من الكائنات البحرية. يقدم للزوار تجارب تعليمية وتفاعلية حول الحياة البحرية.",
    "كورنيش جدة": "كورنيش جدة هو منطقة سياحية ساحلية تمتد على طول 30 كيلومترًا، وتحتوي على أنشطة ترفيهية وأجنحة وفن عام، بما في ذلك المتحف المفتوح للتماثيل الذي يضم أعمالًا لفنانين دوليين."
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