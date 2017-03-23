import json
from os import environ
from os.path import basename, splitext

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

from imagery import (
    CloudSight,
    GoogleVision,
    ImageLabel,
    ImageRecognitionException,
    ImageRecognitionService,
    Rekognition,
)

services = {
    'CloudSight': ImageRecognitionService(
        client=CloudSight,
        options={'threshold': 0.0, 'max_labels': 1}
    ),
    'GoogleVision': ImageRecognitionService(
        client=GoogleVision,
        options={'threshold': 0.8, 'max_labels': 4}
    ),
    'Rekognition': ImageRecognitionService(
        client=Rekognition,
        options={'threshold': 0.8, 'max_labels': 4}
    ),
}

with open(environ['IMAGERY_VISION_API_KEYS_FILE']) as keys_file:
    keys = json.loads(keys_file.read())

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/api/1/<service_name>', methods=['POST'])
def recognize(service_name):

    if service_name not in services:
        return ('Invalid service name', 400)

    if service_name not in keys:
        return ('API credentials not found', 500)

    service = services[service_name]
    api_key = keys[service_name]

    if 'image' not in request.files:
        return ('Image failed to upload', 400)

    f = request.files['image']
    filename = basename(f.filename)
    (_, image_extension) = splitext(filename)

    print image_extension

    options = {}
    for option_name in service.options:
        t = type(service.options[option_name])
        try:
            options[option_name] = t(request.args.get(option_name, service.options[option_name]))
        except ValueError:
            return ('Invalid value for option {}'.format(option_name), 400)

    client = service.client(api_key)
    try:
        search_terms = client.recognize(f.read(), image_extension, **options)
    except ImageRecognitionException as e:
        return (e.message, 400)

    return jsonify(search_terms)
