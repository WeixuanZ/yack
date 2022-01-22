from imutils import face_utils
import numpy as np
import dlib
import cv2


detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(r".\dlib_shape_predictor\shape_predictor_68_face_landmarks.dat")

