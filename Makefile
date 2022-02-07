SHELL := /bin/bash
DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
.PHONY: download-model build
include .secrets

install: download-model
	pip install -r requirements.txt
	pre-commit install

download-model:
	if [ ! -f "$(DIR)/opencv_model/opencv_face_detector_uint8.pb" ]; then \
		wget https://github.com/spmallick/learnopencv/raw/master/AgeGender/opencv_face_detector_uint8.pb -P "$(DIR)/opencv_model/"; \
	fi;
	if [ ! -f "$(DIR)/opencv_model/opencv_face_detector.pbtxt" ]; then \
		wget https://raw.githubusercontent.com/spmallick/learnopencv/master/AgeGender/opencv_face_detector.pbtxt -P "$(DIR)/opencv_model/"; \
	fi;
	if [ ! -f "$(DIR)/opencv_model/haarcascade_frontalface_default.xml" ]; then \
		wget https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml -P "$(DIR)/opencv_model/"; \
	fi;

build:
	docker build -t yack:latest .

run: download-model build
	docker run -e "DEEPGRAM_API_KEY=$(DEEPGRAM_API_KEY)" -e "ENV=production" -p 8000:8000 yack

push: build
	docker tag yack:latest $(CONTAINER_REGISTRY)/yack:latest
	docker push $(CONTAINER_REGISTRY)/yack:latest
