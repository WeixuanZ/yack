SHELL := /bin/bash
DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
.PHONY: download-model build
include .secrets

install: download-model
	pip install -r requirements.txt
	pre-commit install

download-model:
	if [ ! -f "$(DIR)/src/dlib_shape_predictor/shape_predictor_68_face_landmarks.dat" ]; then \
		wget http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2; \
		bzip2 -d shape_predictor_68_face_landmarks.dat.bz2; \
		mv shape_predictor_68_face_landmarks.dat $(DIR)/src/dlib_shape_predictor/; \
	fi;

build:
	docker build -t yack:latest .

run: download-model build
	docker run -e "DEEPGRAM_API_KEY=$(DEEPGRAM_API_KEY)" -p 8000:8000 yack
