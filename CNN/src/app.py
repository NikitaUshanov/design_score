from flask import Flask, request
from flask_cors import CORS
from keras.models import load_model
from cnn_model.custom_objects import layers
from cnn_model.custom_objects import metrics
import json
from preprocess import prepare_image
from typing import Optional, Any
import numpy as np
import tensorflow as tf
from keras.preprocessing.image import ImageDataGenerator
import logging


logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
model: Optional[Any] = None
graph: Optional[Any] = None


def load_cnn_model():
	global model
	model = load_model(
		filepath='cnn_model/design_score.h5',
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


@app.route('/')
def index():
	return "Flask server"


@app.route('/run_cnn', methods=['POST'])
def postdata():
	data = request.get_json()

	image_path = data.get('imagePath')

	input_image = prepare_image(image_path)
	logger.info('Evaluating webpage ...')

	test_datagen = ImageDataGenerator(rescale=1./255)
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
	app.run(host='0.0.0.0', port=5000, debug=True)
