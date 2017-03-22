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
        api_key='cLTgixGfS1Jw-UDLjvWWMg',
        options={'threshold': 0.0, 'max_labels': 1}
    ),
    'GoogleVision': ImageRecognitionService(
        client=GoogleVision,
        api_key='AIzaSyAPmJ_b6brvmCFT_rmUu_VSJM4By2Cqhp8',
        options={'threshold': 0.8, 'max_labels': 4}
    ),
    'Rekognition': ImageRecognitionService(
        client=Rekognition,
        api_key={
            'access_key_id': 'AKIAJQXQUOV6ZVPRGV7A',
            'secret_key': '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',
        },
        options={'threshold': 0.8, 'max_labels': 4}
    ),
}

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/api/1/<service_name>', methods=['POST'])
def recognize(service_name):
    if service_name not in services:
        pass

    print request.files.keys()

    service = services[service_name]

    f = request.files['image']
    print f
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

    print 'ddd'

    client = service.client(service.api_key)
    try:
        search_terms = client.recognize(f.read(), image_extension, **options)
    except ImageRecognitionException as e:
        return (e.message, 400)

    print 'eee'
    return jsonify(search_terms)
