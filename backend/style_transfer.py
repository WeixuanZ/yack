import cv2
import numpy as np

class StyleTransfer:
    def __init__(self):
        self.LINE_SIZE = 7
        self.BLUR_VALUE = 7
        self.TOTAL_COLOR = 9

    def __call__(self, raw_img):
        img = self.preprocess_img(raw_img)
        edges = self.edge_mask(img)
        img = self.color_quantization(img, self.TOTAL_COLOR)
        blurred = cv2.bilateralFilter(img, d=7, sigmaColor=200,sigmaSpace=200)
        styled_img = cv2.bitwise_and(blurred, blurred, mask=edges)
        return styled_img

    def preprocess_img(self, img):
        # TODO: add size and resolution standardization
        return img

    def color_quantization(self, img, k):
        # Transform the image
        data = np.float32(img).reshape((-1, 3))

        # Determine criteria
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.001)

        # Implementing K-Means
        ret, label, center = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        center = np.uint8(center)
        result = center[label.flatten()]
        result = result.reshape(img.shape)
        return result

    def edge_mask(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray_blur = cv2.medianBlur(gray, self.BLUR_VALUE)
        edges = cv2.adaptiveThreshold(gray_blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, self.LINE_SIZE, self.BLUR_VALUE)
        return edges


