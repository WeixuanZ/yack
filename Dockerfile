FROM ubuntu:20.04
LABEL version="0.1"
LABEL description="Docker image for YACK"
ARG DEBIAN_FRONTEND=noninteractive

RUN apt update
RUN apt install -y python3-pip python3-dev cmake ffmpeg libsm6 libxext6 wget

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 8000
CMD ["gunicorn", "--bind", ":8000", "--workers", "2", "--threads", "8", "--timeout", "0", "--pythonpath", "./src", "main:app"]
