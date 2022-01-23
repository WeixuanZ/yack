FROM ubuntu:20.04
LABEL version="0.1"
LABEL description="Docker image for YACK"
ARG DEBIAN_FRONTEND=noninteractive

RUN apt update
RUN apt install -y python3-pip python3-dev cmake ffmpeg libsm6 libxext6

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

EXPOSE 8000
CMD ["python3", "/app/src/main.py"]
