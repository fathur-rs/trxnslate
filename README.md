# TRxNSLATE API: OCR + LLMs for Explaining Handwritten Medical Prescriptions

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.9-blue.svg?style=flat-square)](https://www.python.org/downloads/release/python-390/)
[![Docker Compose](https://img.shields.io/badge/Docker%20Compose-Supported-blue?style=flat-square&logo=docker)](https://docs.docker.com/compose/)

This program utilizes optical character recognition (OCR) system to extract and digitize handwritten text from medical prescription images. It employs YOLOv10 to detect and highlight critical elements within the prescription, such as drug names, instructions, and dosages. These detected segments are then cropped and processed using Transformer Optical Character Recognition (TrOCR), which converts the handwritten segments into digital text. Finally, the digitized prescription text is passed to a Large Language Model, primarily using LLama 3.1 70B, with extensive prompt engineering to generate easy-to-understand explanations of the prescription.

This project specifically aims to support the Indonesian prescription format and language. It helps patients who struggle to read medical prescriptions due to lack of expertise or poor handwriting from doctors. Additionally, it offers the potential to streamline healthcare workflows by automating the prescription review process, thereby enhancing efficiency and accuracy in medical care.

## Installation Guide

### 1. Clone the repository
```bash
git clone https://github.com/fathur-rs/trxnslate.git
cd trxnslate
```

### 2. Rename `.env.example` to `.env`
```bash
mv .env.example .env
```

### 3. Edit the environment file
You can obtain the NVIDIA AI Foundation API key from [NVIDIA](https://build.nvidia.com/explore/discover#llama-3_1-8b-instruct).

Update your `.env` file with the following:
```bash
FLASK_DEBUG=
FLASK_RUN_PORT=
FLASK_RUN_HOST=

NVIDIA_API_KEY=
SQLALCHEMY_DATABASE_URI=
JWT_SECRET_KEY=
```

### 4. Running locally
Use any environment management tool, preferably Conda.

```bash
# Create a new Conda environment
conda create -n trxnslate python=3.9

# Activate the Conda environment
conda activate trxnslate

# Install requirements
pip install -r requirements.txt

# Run the Flask application
python run.py
```

### 5. Install & Run via Docker Compose
Ensure Docker and Docker Compose are installed on your system.

```bash
docker-compose up --build
```

The program will run on port `8000` and localhost.


## Endpoints Documentation
Refer to the [Swagger UI](http://localhost:8000/api/swagger) to try the API directly.
### 1.  Register User

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

### 2.  User Login

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

### 3.  List All Users (Active Admin only)

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

### 4.  Soft Delete a User (Active Admin only)

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


### 5.  Perform OCR on an Input Image

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

### 6.  Generate LLM Explanations from Prescription Text

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
  

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.


## Contact
For any inquiries or feedback, please contact:
- Email: fathurrahmansyarief@gmail.com
- LinkedIn: [Fathurrahman Syarief](https://www.linkedin.com/in/fathurrahman-syarief/)

