FROM python:3.8

COPY requirements.txt .
COPY doctorrx-387716-cdaefd627b4a.json .

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN pip install -r requirements.txt 
