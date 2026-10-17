import cv2
import numpy as np
from sklearn.externals import joblib

class ImageRecognitionModel:
    def __init__(self, model_path):
        self.model = joblib.load(model_path)

    def preprocess_image(self, image_path):
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = cv2.resize(image, (128, 128))  # Resize to match model input
        image = image / 255.0  # Normalize the image
        return image.reshape(1, 128, 128, 1)  # Reshape for the model

    def predict(self, image_path):
        processed_image = self.preprocess_image(image_path)
        prediction = self.model.predict(processed_image)
        return prediction

# Example usage:
# model = ImageRecognitionModel('path/to/your/model.pkl')
# result = model.predict('path/to/image.jpg')
# print(result)