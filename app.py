from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import base64
from io import BytesIO
from PIL import Image
import joblib
import os
import io

app = FastAPI()

# Allow CORS for local React development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Load models at startup
print("Loading pre-trained models...")
try:
    scaler = joblib.load('models/scaler.pkl')
    knn = joblib.load('models/knn.pkl')
    log_reg = joblib.load('models/log_reg.pkl')
    svm = joblib.load('models/svm.pkl')
    print("Models loaded successfully.")
except Exception as e:
    print(f"Warning: Failed to load models: {e}. Please run train_models.py first.")

class ImageData(BaseModel):
    image: str # Base64 encoded string from React canvas

def add_adversarial_noise(X_scaled, epsilon=1.0):
    # sign of gaussian noise times epsilon just like in main.py
    # Re-seed to ensure output consistency if needed, but here it's fine random
    noise = epsilon * np.sign(np.random.randn(*X_scaled.shape))
    X_scaled_adv = X_scaled + noise
    return X_scaled_adv

def preprocess_image(base64_img):
    # Remove header if present (e.g. data:image/png;base64,)
    if ',' in base64_img:
        base64_img = base64_img.split(',')[1]
        
    img_data = base64.b64decode(base64_img)
    img = Image.open(BytesIO(img_data))
    
    # We expect the canvas to send RGBA, often with transparent bg.
    # MNIST digits are white on a black background.
    # Let's create a black background
    background = Image.new('RGBA', img.size, (0, 0, 0, 255))
    # Paste using alpha channel as mask
    background.paste(img, (0, 0), img)
    
    # Convert to grayscale
    gray = background.convert('L')
    
    # Resize to 28x28 using Lanczos
    resized = gray.resize((28, 28), Image.Resampling.LANCZOS)
    
    # Convert to numpy array and normalize to [0, 1]
    img_array = np.array(resized) / 255.0
    
    # Flatten array (1, 784)
    flat_array = img_array.reshape(1, -1)
    return flat_array

@app.post("/predict")
async def predict(data: ImageData):
    try:
        # 1. Preprocess
        img_flat = preprocess_image(data.image)
        
        # 2. Scale via standard scaler
        X_scaled = scaler.transform(img_flat)
        
        # 3. Clean Predictions
        clean_preds = {
            "KNN": int(knn.predict(X_scaled)[0]),
            "Logistic Regression": int(log_reg.predict(X_scaled)[0]),
            "SVM": int(svm.predict(X_scaled)[0])
        }
        
        # 4. Generate Adversarial Noisy Image
        X_adv_scaled = add_adversarial_noise(X_scaled, epsilon=1.0)
        
        # 5. Adversarial Predictions
        adv_preds = {
            "KNN": int(knn.predict(X_adv_scaled)[0]),
            "Logistic Regression": int(log_reg.predict(X_adv_scaled)[0]),
            "SVM": int(svm.predict(X_adv_scaled)[0])
        }
        
        return {
            "status": "success",
            "clean_predictions": clean_preds,
            "adversarial_predictions": adv_preds,
            "message": "Predictions completed successfully."
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/")
def read_root():
    return {"message": "MNIST Model Server Running"}
