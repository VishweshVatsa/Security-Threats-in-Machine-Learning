# Server hot-reload triggered
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
    img_array = np.array(gray)
    
    # Find bounding box of the non-black regions (threshold > 15 avoids anti-aliasing dust)
    non_empty_columns = np.where(img_array.max(axis=0) > 15)[0]
    non_empty_rows = np.where(img_array.max(axis=1) > 15)[0]
    
    # If the user drew nothing, return zeros
    if len(non_empty_columns) == 0 or len(non_empty_rows) == 0:
        return np.zeros((1, 784))
        
    min_x, max_x = non_empty_columns[0], non_empty_columns[-1]
    min_y, max_y = non_empty_rows[0], non_empty_rows[-1]
    
    # Crop the image to exactly the drawn digit
    cropped_array = img_array[min_y:max_y+1, min_x:max_x+1]
    
    # Resize the image so its max dimension is 20 pixels
    cropped_img = Image.fromarray(cropped_array)
    width, height = cropped_img.size
    
    if width > height:
        new_width = 20
        new_height = max(1, int(20 * (height / width)))
    else:
        new_height = 20
        new_width = max(1, int(20 * (width / height)))
        
    # Using BICUBIC as LANCZOS can create negative clipping artifacts 
    resized_cropped = cropped_img.resize((new_width, new_height), Image.Resampling.BICUBIC)
    resized_array = np.array(resized_cropped)
    
    # Create the 28x28 padded result array
    final_array = np.zeros((28, 28), dtype=np.uint8)
    
    # Calculate center of mass (cast to float to explicitly avoid uint8 overflow precision loss)
    mass_array = resized_array.astype(np.float32)
    y_coords, x_coords = np.indices(mass_array.shape)
    total_mass = np.sum(mass_array)
    
    if total_mass > 0:
        center_y = int(np.round(np.sum(y_coords * mass_array) / total_mass))
        center_x = int(np.round(np.sum(x_coords * mass_array) / total_mass))
    else:
        center_y, center_x = new_height // 2, new_width // 2
        
    # We want the center of mass to map to (14, 14) in the final image
    start_y = 14 - center_y
    start_x = 14 - center_x
    
    # Constrain within boundaries so we don't slice out of bounds
    start_y = max(0, min(start_y, 28 - new_height))
    start_x = max(0, min(start_x, 28 - new_width))
    
    end_y = start_y + new_height
    end_x = start_x + new_width
    
    final_array[start_y:end_y, start_x:end_x] = resized_array
    
    # Convert to float and normalize to [0, 1]
    final_img_array = final_array / 255.0
    
    # Flatten array (1, 784)
    flat_array = final_img_array.reshape(1, -1)
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
