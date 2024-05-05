import numpy as np
import cv2

width = 256
height = 192
channels = 3


def prepare_image(image_path):

    X = [cv2.resize(
        cv2.imread(image_path, cv2.IMREAD_COLOR),
        (width, height),
        interpolation=cv2.INTER_AREA,
    )]

    return np.array(X)
