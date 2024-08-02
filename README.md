# TRxNSLATE API: OCR + LLMs for explaining handwritten medical prescription

## Overview
This program utilizes advanced optical character recognition (OCR) to extract and digitize handwritten text from medical prescription images. It employs YOLOv10 to detect and highlight critical elements within the prescription, such as drug names, instructions, and dosages. These detected segments are then cropped and processed using Transformer Optical Character Recognition (TrOCR), which converts the handwritten segments into digital text. Finally, the digitized prescription text is passed to a Large Language Model, primarily using LLama 3.1 70B, with extensive prompt engineering to generate the output in a specific format.

This project specifically aims to support the Indonesian prescription format and language. It helps patients who struggle to read medical prescriptions due to lack of expertise or poor handwriting from doctors. Additionally, it offers the potential to streamline healthcare workflows by automating the prescription review process, thereby enhancing efficiency and accuracy in medical care.

## Endpoints Documentation
This is the TRxNSLATE API endpoint documentation
### Register User

- **Method:** POST
- **URL:** `http://localhost:8000/api/auth/register`
- **Description:** Register new user
- **Request Body (parameters):**

  ```json
  {
    "username": "string (required, minLength: 1, maxLength: 80, pattern: ^[a-zA-Z0-9_]+$)",
    "password": "string (required, minLength: 12, pattern: ^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&])[A-Za-z\\d@$!%*?&]{12,}$)"
  }
  ```

- **Response Body (responses):**

  - **201:** User created successfully
  - **400:** Bad Request - Invalid username or password
  - **409:** Conflict - User already exists or constraint violation
  - **500:** Internal Server Error - An error occurred during registration

---

### User Login

- **Method:** POST
- **URL:** `http://localhost:8000/api/auth/login`
- **Description:** User login
- **Request Body (parameters):**

  ```json
  {
    "username": "string (required)",
    "password": "string (required)",
    "user_type": "string (required, enum: [user, admin])"
  }
  ```

- **Response Body (responses):**

  - **200:** Successful login

    ```json
    {
      "access_token": "string",
      "refresh_token": "string",
      "user_type": "string (enum: [user, admin])"
    }
    ```

  - **400:** Bad Request - No data provided or Invalid JSON data
  - **401:** Unauthorized - Invalid credentials
  - **500:** Internal Server Error - An error occurred during login

---

### List All Users (Active Admin only)

- **Method:** GET
- **URL:** `http://localhost:8000/api/auth/users`
- **Description:** List all users (Active Admin only)
- **Request Body (parameters):**

  - **Header:**

    ```json
    {
      "Authorization": "string (required, format: Bearer {token})"
    }
    ```

- **Response Body (responses):**

  - **200:** Successful retrieval of users list

    ```json
    [
      {
        "id": "integer",
        "username": "string"
      }
    ]
    ```

  - **401:** Unauthorized - Invalid or missing token, or missing 'Bearer' prefix
  - **403:** Forbidden - User is not an active admin
  - **500:** Internal Server Error - An error occurred while retrieving users

---

### Soft Delete a User (Active Admin only)

- **Method:** DELETE
- **URL:** `http://localhost:8000/api/auth/delete_user/`
- **Description:** Soft delete a user (Active Admin only)
- **Request Body (parameters):**

  - **Header:**

    ```json
    {
      "Authorization": "string (required, format: Bearer {token})"
    }
    ```

  - **Query:**

    ```json
    {
      "id": "integer (required)"
    }
    ```

- **Response Body (responses):**

  - **200:** User deleted successfully
  - **400:** Bad Request - No user ID provided
  - **401:** Unauthorized - Invalid or missing token, or missing 'Bearer' prefix
  - **403:** Forbidden - User is not an active admin
  - **404:** Not Found - Admin not found or User does not exist
  - **409:** Conflict - User deletion failed due to a constraint violation
  - **500:** Internal Server Error - An error occurred during deleting user

---

### Perform OCR on an Input Image

- **Method:** POST
- **URL:** `http://localhost:8000/api/model/ocr`
- **Description:** Perform OCR on an input image
- **Request Body (parameters):**

  - **Header:**

    ```json
    {
      "Authorization": "string (required, format: Bearer {token})"
    }
    ```

  - **Body:**

    ```json
    {
      "image": "string (required, Base64 encoded image data)"
    }
    ```

- **Response Body (responses):**

  - **200:** Image processed successfully

    ```json
    {
      "image": "string (Base64 encoded processed image with OCR annotations)",
      "prescription_text": "string (Extracted text from the image)"
    }
    ```

  - **400:** Bad Request - No image data in the request or error processing image
  - **401:** Unauthorized - Invalid or missing token, or missing 'Bearer' prefix
  - **500:** Internal Server Error - An error occurred during OCR processing

---

### Generate LLM Explanations from Prescription Text

- **Method:** POST
- **URL:** `http://localhost:8000/api/model/generate_prescription_explanations`
- **Description:** Generate LLM explanations from prescription text
- **Request Body (parameters):**

  - **Header:**

    ```json
    {
      "Authorization": "string (required, format: Bearer {token})"
    }
    ```

  - **Body:**

    ```json
    {
      "prescription_text": "string (required, Prescription text for analysis)"
    }
    ```

- **Response Body (responses):**

  - **200:** Explanations generated successfully

    ```json
    {
      "explanation": "string (Generated explanation of the prescription)"
    }
    ```

  - **400:** Bad Request - No prescription text in the request or error generating explanations
  - **401:** Unauthorized - Invalid or missing token, or missing 'Bearer' prefix
  - **500:** Internal Server Error - An error occurred during explanation generation