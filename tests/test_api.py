# pylint: disable=missing-docstring, import-error, redefined-outer-name
# Note: I'm suppressing redefined-outer-name because pytest fixtures use
# the same fixture name and parameter name by convention.
''' These tests may assume certain results from certain services. These results
seem very stable, but are not guaranteed. So failing tests DO NOT imply bad
code. But passing tests are a good indication that all is right with the
world.'''

import pytest
from werkzeug.datastructures import FileMultiDict

@pytest.fixture(params=["GoogleVision", "Rekognition", "CloudSight"])
def recognition_service(request):
    yield request.param

@pytest.fixture(params=[
    {
        'file': 'chess.jpg',
        'GoogleVision': 'chess',
        'Rekognition': 'clock',
        'CloudSight': 'hat',
    },
    {
        'file': 'cat.jpg',
        'GoogleVision': 'cat',
        'Rekognition': 'cat',
        'CloudSight': 'cat',
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
    print 'vvvv Response data vvvvvvvvvvvvvv'
    print resp.data
    print '^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^'
    assert resp.status_code == 200
    keywords = []
    results = resp.json
    words = [str(word).lower().split(' ') for word in results['search_terms']]
    for word_list in words:
        keywords += word_list
    assert image[recognition_service] in keywords

    if recognition_service == 'CloudSight':
        keywords = [str(subject).lower().split(' ')[-1] for subject in results['subjects']]
        assert image[recognition_service] in keywords
