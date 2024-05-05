from flask import Flask, request
from flask_cors import CORS
from keras.models import load_model
from cnn_model.custom_objects import layers
from cnn_model.custom_objects import metrics
import json
from preprocess import prepare_image
import numpy as np
import tensorflow as tf
from keras.preprocessing.image import ImageDataGenerator
from typing import Optional, Any
import logging
import base64
from io import BytesIO
from PIL import Image

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
model: Optional[Any] = None
graph: Optional[Any] = None


def load_cnn_model():
    global model
    model = load_model(
        'cnn_model/design_score.h5',
        custom_objects={
            'LRN': layers.LRN,
            'euclidean_distance_loss': metrics.euclidean_distance_loss,
            'rmse': metrics.rmse,
        }
    )
    model.summary()
    logger.info('[*] Model loaded')
    global graph
    graph = tf.get_default_graph()


def decode_image(encoded_string):
    image_data = base64.b64decode(encoded_string)
    image = Image.open(BytesIO(image_data))
    image.save('image-tmp/decoded_image.png')


@app.route('/')
def index():
    return "ML-engine"


@app.route('/run_cnn', methods=['POST'])
def postdata():
    data = request.get_json()

    decode_image(data.get("image"))

    input_image = prepare_image("image-tmp/decoded_image.png")
    logger.info('Evaluating webpage ...')

    test_datagen = ImageDataGenerator(rescale=1. / 255)
    test_data = test_datagen.flow(input_image, batch_size=1, shuffle=False).next()

    with graph.as_default():
        score = model.predict(test_data)
        score = float(score)

        # score bound protection
        score = np.minimum(score, 10.0)
        score = np.maximum(score, 1.0)

        logger.info('CNN score: ' + str(score))

    return json.dumps({"score": score})


if __name__ == "__main__":
    load_cnn_model()
    app.run(host='0.0.0.0', port=7000, debug=True)
