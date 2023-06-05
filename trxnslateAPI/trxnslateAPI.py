from fastapi import FastAPI 
from pydantic import BaseModel
from typing import Union
import uvicorn

app = FastAPI()


@app.get("/")
async def welcome_page():
    return {
        "message": "Welcome to DoctorRX API"
    }
    
@app.get("/model/download/{version}")
async def download_latest_model(version:float):
    
    from google.cloud import storage
    import os
    

    print("<=== initiate os env gcp creds ====>")
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'doctorrx-387716-cdaefd627b4a.json'

    #bucket
    print('<=== get bucket ===>')
    storage_client = storage.Client()
    bucket = storage_client.get_bucket('doctorrx_pipeline_bucket')
    blob = bucket.blob("models/{version}/model.h5")
    blob.download_to_filename("models/model.5")
    
    
    return {
        "message": "Berhasil mengupdate model!"
    }
    
class ImagesPrediction(BaseModel):
    img_array: Union[list, None] = None

@app.post("/prediction")
async def predict_vgg16(item: ImagesPrediction):
    
    from keras.applications.vgg16 import VGG16
    from keras.models import Model
    from tensorflow.keras.models import load_model
    import numpy as np
    import cv2
    from tensorflow.keras.applications.vgg16 import decode_predictions


    
    # CONVERT LIST TO NUMPY ARRAY
    conv_array = np.asarray(item.img_array, dtype='uint8')
    image = cv2.resize(conv_array, (200, 100)) 
    blur = cv2.GaussianBlur(image, (5,5), 0)
    ret3,th3 = cv2.threshold(blur.astype(np.uint8),0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    to_rgb_array = np.repeat(th3[..., np.newaxis], 3, -1).reshape(1, 100, 200 , 3)
    to_rgb_array = to_rgb_array / 255
        
    # VGG FEATURES         
    model_vgg16 = VGG16(weights='imagenet', include_top=False)
    model_vgg16 = Model(inputs=model_vgg16.inputs, outputs=model_vgg16.layers[-4].output)
    
    features = model_vgg16.predict(to_rgb_array)
    
    # LOAD MODEL

    #fine tuning vgg
    model = load_model("models/model.h5")

    # model 2
    pred = model.predict(features)
    prediction = np.argmax(pred)
    # 0.9880239520958084
    print(pred)
    print(np.max(pred))
        
    labels = {
        0: 'Paracetamol',
        1: 'Amoxilin',
        2: 'CTM',
        3: 'Amlodipin',
        4: 'Metformin' }

    return {
            "predict": labels[int(prediction)]
            }
    