from flask import url_for
import pytest
from werkzeug.datastructures import FileMultiDict

@pytest.fixture(params=["GoogleVision", "Rekognition", "CloudSight"])
def recognition_service(request):
	yield request.param

@pytest.fixture(params=[
	{
		'file': 'nicestar.jpg',
		'GoogleVision': 'star',
		'Rekognition': 'origami',
		'CloudSight': 'star'
	},
	{
		'file': 'cat.jpg',
		'GoogleVision': 'cat',
		'Rekognition': 'cat',
		'CloudSight': 'cat'
	},
])
def image(request):
    yield request.param

def test_services(client, recognition_service, image):
	print recognition_service
	code = client.get('/').status_code
	assert code == 200
	with open('test_images/{}'.format(image['file']), 'rb') as f:
		d = FileMultiDict()
		d.add_file('image', f, image['file'])
		resp = client.post('/api/1/{}'.format(recognition_service), data=d)
	print resp.json
	keywords = []
	for word in resp.json:
        # Account for CloudSight returning a single keyword of the form
        # "descriptive phrase".
		words = [str(word).lower().replace('"', '').split(' ') for word in resp.json]
		for word_list in words:
			keywords += word_list
	assert image[recognition_service] in keywords
