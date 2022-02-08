FROM python:3
LABEL version="0.1"
LABEL description="Docker image for YACK"

RUN apt update && apt install -y ffmpeg libsm6 libxext6 wget

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

RUN make download-model

EXPOSE 8000
CMD ["gunicorn", "--bind", ":8000", "--workers", "2", "--threads", "8", "--timeout", "0", "--pythonpath", "./src", "main:app"]
