from pydantic import BaseModel, field_validator
import base64
import binascii
    
class InputImageBase64(BaseModel):
    image: str
    
    @field_validator('image')
    def validate_base64_image(cls, v):
        """Check if the image is base64 encoded or just a random string"""
        try:
            # Try to decode the string as base64
            decoded = base64.b64decode(v)
            
            # Check if the decoded string starts with known image file signatures
            # This is a basic check and doesn't guarantee the image is valid,
            # but it helps filter out random strings
            if decoded.startswith(b'\xff\xd8\xff') or \
                decoded.startswith(b'\x89PNG\r\n\x1a\n') or \
                decoded.startswith(b'GIF87a') or  \
                decoded.startswith(b'GIF89a'):  # JPEG or PNG or GIF (in order)
                return v
            else:
                raise ValueError("Decoded string is not a recognized image format")
        except binascii.Error:
            raise ValueError("Invalid base64 encoding")
        except Exception as e:
            raise ValueError(f"Error validating base64 image: {str(e)}")
        
class PrescriptionText(BaseModel):
    prescription_text: str
    
    
    
