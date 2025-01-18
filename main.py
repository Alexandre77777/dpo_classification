from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import numpy as np
from PIL import Image
import pickle
from skimage.feature import hog
from skimage.transform import resize
from sklearn.preprocessing import StandardScaler
from io import BytesIO

app = FastAPI()

# Загрузка модели и scaler
with open('best_classification_model.pkl', 'rb') as f:
    model = pickle.load(f)

with open('scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

def extract_features(image):
    # Изменение размера изображения до 28x28 (размер MNIST)
    img_resized = resize(image, (28, 28), anti_aliasing=True)
    
    # Преобразование изображения в оттенки серого
    if len(img_resized.shape) == 3:
        img_gray = np.mean(img_resized, axis=2)
    else:
        img_gray = img_resized
    
    # Вычисление HOG-дескриптора
    hog_features = hog(
        img_gray, 
        orientations=9, 
        pixels_per_cell=(8, 8),
        cells_per_block=(2, 2), 
        visualize=False
    )
    
    return hog_features

@app.post("/predict/")
async def predict(file: UploadFile = File(...)):

    # Чтение исходных байтов файла
    contents = await file.read()
        
    # Открываем изображение через BytesIO
    image = Image.open(BytesIO(contents))
    
    # Извлечение признаков
    features = extract_features(np.array(image))
    
    # Масштабирование признаков
    features_scaled = scaler.transform([features])
    
    # Предсказание
    prediction = model.predict(features_scaled)
    
    return JSONResponse(content={"prediction": int(prediction[0])})