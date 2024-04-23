# -*- coding: utf-8 -*-
"""Untitled8.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1psfPbz30jEuKFLSL4pmx0QEwN3xho3iQ
"""

from roboflow import Roboflow
import supervision as sv
import cv2

rf = Roboflow(api_key="l50pY8a1y9SHUGlnCUl7")
project = rf.workspace().project("ovos-de-parasitas-azoug")
model = project.version(6).model

# Returnns the count (int) of parasite eggs
def predict(file_path):
    result = model.predict(file_path, confidence=40, overlap=30).json()
    detections = sv.Detections.from_roboflow(result)
    return detections.class_id.size

# labels = [item["class"] for item in result["predictions"]]

# label_annotator = sv.LabelAnnotator()
# bounding_box_annotator = sv.BoxAnnotator()

# image = cv2.imread("Enterobius-Vermicularis-151-_jpg.rf.4c92700ee3c56f6c90efe5f27003279a.jpg")

# annotated_image = bounding_box_annotator.annotate(
#     scene=image, detections=detections)
# annotated_image = label_annotator.annotate(
#     scene=annotated_image, detections=detections, labels=labels)

# print(detections.class_id.size, "parasite eggs detected")

# sv.plot_image(image=annotated_image, size=(16, 16))