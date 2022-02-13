FROM python:3
LABEL version="0.2"
LABEL description="Docker image for yack!"

RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN mkdir /app/uploads

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

ADD https://github.com/spmallick/learnopencv/raw/master/AgeGender/opencv_face_detector_uint8.pb                     /app/opencv_model/
ADD https://raw.githubusercontent.com/spmallick/learnopencv/master/AgeGender/opencv_face_detector.pbtxt             /app/opencv_model/
ADD https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml    /app/opencv_model/
COPY src/ /app/src/

EXPOSE 8000
CMD ["gunicorn", "--bind", ":8000", "--workers", "2", "--threads", "8", "--timeout", "0", "--pythonpath", "./src", "main:app"]
