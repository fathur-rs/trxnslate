import logging
import os
import base64
import numpy as np
from functools import lru_cache
from typing import List, Tuple

import cv2
import torch
from ultralytics import YOLOv10
from transformers import VisionEncoderDecoderModel, TrOCRProcessor
from huggingface_hub.utils import RepositoryNotFoundError
from huggingface_hub import model_info

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(name)s - %(message)s", level=logging.INFO)

class OCRHelper:
    @staticmethod
    def calculate_iou(box1: List[float], box2: List[float]) -> float:
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])

        intersection_area = max(0, x2 - x1) * max(0, y2 - y1)
        box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
        box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
        union_area = box1_area + box2_area - intersection_area

        return intersection_area / union_area if union_area > 0 else 0

    @staticmethod
    def filter_similar_boxes(sorted_detections: List[Tuple], iou_threshold: float = 0.7) -> List[Tuple]:
        filtered_detections = []
        while sorted_detections:
            current = sorted_detections.pop(0)
            filtered_detections.append(current)
            sorted_detections = [
                other for other in sorted_detections
                if OCRHelper.calculate_iou(current[0], other[0]) < iou_threshold
            ]
        return filtered_detections

    @staticmethod
    def convert_image_to_base64(image: np.ndarray) -> str:
        _, encoded_image = cv2.imencode(".jpg", image)
        return base64.b64encode(encoded_image).decode("utf-8")

class OpticalCharacterRecognition:
    LABEL_MAP = {0: "Prescriptio", 1: "Signatura"}

    def __init__(self):
        self.cwd = os.getcwd()
        logging.info(f"📂 Current Working Directory: {self.cwd}")
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logging.info(f"⚡ Acceleration Used: {self.device}")
        
        self.model_trocr = self.load_trocr_model()
        self.processor_trocr = TrOCRProcessor.from_pretrained("microsoft/trocr-large-handwritten")
        self.model_yolo = self.load_yolo_model()

    @lru_cache(maxsize=1)
    def load_trocr_model(self):
        model_source_path = "fathurfrs/trocr-large-handwritten-prescription"
        logging.info(f"📂 TrOCR model HuggingFace repository: {model_source_path}")
        try:
            model_info(model_source_path)
            return VisionEncoderDecoderModel.from_pretrained(model_source_path).to(self.device)
        except RepositoryNotFoundError:
            raise FileNotFoundError(f"❌ TrOCR model not found at https://huggingface.co/{model_source_path}")

    @lru_cache(maxsize=1)
    def load_yolo_model(self):
        absolute_path = os.path.join(self.cwd, "ml_model/yolov10/best.pt")
        logging.info(f"📂 YOLO model local path: {absolute_path}")
        if os.path.exists(absolute_path):
            return YOLOv10(absolute_path)
        else:
            raise FileNotFoundError(f"❌ YOLO model not found at {absolute_path}")

    @torch.no_grad()
    def predict_trocr(self, image: np.ndarray) -> str:
        pixel_values = self.processor_trocr(image, return_tensors="pt").pixel_values.to(self.device)
        generated_ids = self.model_trocr.generate(pixel_values)
        return self.processor_trocr.batch_decode(generated_ids, skip_special_tokens=True)[0].replace(".jpg", "")
    
    def inferencing(self, image: np.ndarray, detections) -> Tuple[str, List[str]]:
        detection_data = list(zip(detections.xyxy, detections.confidence, detections.class_id))
        sorted_detections = sorted(detection_data, key=lambda x: x[0][1])
        filtered_detections = OCRHelper.filter_similar_boxes(sorted_detections)

        prescription_text = []
        for box, confidence, class_id in filtered_detections:
            x1, y1, x2, y2 = map(int, box)
            
            crop_img = image[y1:y2, x1:x2]
            gen = self.predict_trocr(crop_img)
            prescription_text.append(gen)
            
            color = (0, 255, 0) if class_id == 0 else (255, 0, 0)
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
            label = f"Class {self.LABEL_MAP[class_id]}: {confidence:.2f}"
            cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        image_draw_bbox = OCRHelper.convert_image_to_base64(image)
        
        return image_draw_bbox, prescription_text