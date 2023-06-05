FROM python:3.8

ENV PYTHONUNBUFFERED True

COPY . ./

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN pip install --no-cache-dir -r requirements.txt

CMD uvicorn doctorrxAPI:app --port=8000 --host=0.0.0.0
