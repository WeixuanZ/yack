FROM python:3
LABEL version="0.2"
LABEL description="Docker image for yack!"

RUN apt update && apt install -y ffmpeg libsm6 libxext6 wget

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

COPY ./.secrets         /app/.secrets
COPY ./Makefile         /app/Makefile
COPY ./opencv_model/    /app/opencv_model/
COPY ./src/             /app/src/

RUN make download-model
RUN mkdir /app/uploads

EXPOSE 8000
CMD ["gunicorn", "--bind", ":8000", "--workers", "2", "--threads", "8", "--timeout", "0", "--pythonpath", "./src", "main:app"]
