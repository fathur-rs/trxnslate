import logging
from flask import request
from flask_jwt_extended import jwt_required
from app.api import model_blueprint
from ml_model.large_language_models import Llama3_1_70B
from ml_model.optical_character_recognition import OpticalCharacterRecognition
from ..utilities import (make_response_util, 
                         base64_to_pil,
                         pil_to_cv2)
import supervision as sv
from ..models.apiSchema import InputImageBase64, PrescriptionText

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ocr = OpticalCharacterRecognition()
llm = Llama3_1_70B()

@model_blueprint.route('/ocr', methods=['POST'])
@jwt_required()
def input_image():
    """Do an OCR from input image."""
    logger.info("📥 Received request for OCR")

    if 'image' not in request.json:
        logger.warning("⚠️ No image data in the request")
        return make_response_util(400, description="No image data in the request", error='Bad Request')
    
    base64_image = InputImageBase64(**request.get_json())
    try:
        logger.info("🖼️ Converting base64 image to PIL format")
        pil_image = base64_to_pil(base64_image.image)
        
        logger.info("🔄 Converting PIL image to cv2 format")
        cv2_image = pil_to_cv2(pil_image)
        
        logger.info("🔍 Performing OCR")
        do_ocr = ocr.model_yolo(source=cv2_image, conf=0.25, iou=0.45, agnostic_nms=True)[0]
        do_detections = sv.Detections.from_ultralytics(do_ocr)
        
        logger.info("🧠 Inferencing OCR results")
        output_image, output_text = ocr.inferencing(cv2_image.copy(), do_detections)
        
        structured_output_text = "\n".join(output_text)
        
        result = {
            "image": output_image,
            "text": structured_output_text
        }
        
        logger.info("✅ OCR processing completed successfully")
        return make_response_util(200, description="Image processed successfully", message=result)
    except Exception as e:
        logger.error(f"❌ Error processing image: {str(e)}")
        return make_response_util(400, description=f"Error processing image: {str(e)}", error='Bad Request')


@model_blueprint.route('/generate_prescription_explanations', methods=['POST'])
@jwt_required()
def generate_prescription_explanations():
    """Generate LLM explanations from OCR outputs."""
    logger.info("📥 Received request for generating prescription explanations")

    if 'prescription_text' not in request.json:
        logger.warning("⚠️ No prescription text in the request")
        return make_response_util(400, description="No prescription text in the request", error='Bad Request')
    
    prescription_text = PrescriptionText(**request.get_json())
    try:
        logger.info("🧠 Generating prescription explanations")
        do_generate_prescription_explanations = llm.analyze_prescription(prescription_text.prescription_text)
        
        logger.info("✅ Explanations generated successfully")
        return make_response_util(200, description="Explanations generated successfully", message=do_generate_prescription_explanations)
        
    except Exception as e:
        logger.error(f"❌ Error generating explanations: {str(e)}")
        return make_response_util(400, description=f"Error generating explanations: {str(e)}", error='Bad Request')
