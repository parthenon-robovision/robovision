""" Tools for recognizing images via cloud services.

Example:
    client_instance = CloudSight('XXXAPIKEYXXX')
    all_image_labels = client_instance.recognize(
        image_data,
        '.jpg',
        threshold=0.8,
        max_labels=5
    )
"""

from collections import namedtuple

import boto3
from botocore.exceptions import ClientError
import cloudsight
from cloudsight.errors import APIError
from google.cloud import vision as googlevision # pylint: disable=import-error
from google.cloud.exceptions import GoogleCloudError # pylint: disable=import-error

# A ranked label has two parts: a label and a relevance rating (rank).
# Relevance ratings vary from service to service and should be on a range 0 to 1
# inclusive, where 1 is the best match and 0 is the worst possible match.
ImageLabel = namedtuple('ImageLabel', ['label', 'rank'])

# An image service has a client class that accepts an api_key on instantiation.
# Options can be any dictionary from keywords to primitive values.
ImageRecognitionService = namedtuple(
    'ImageRecognitionService',
    ['client', 'options']
)

class ImageRecognitionException(Exception):
    """Thrown when we are unable, for any reason, to recognize an image."""
    pass


class ImageRecogonitionService(object):
    """Framework for recognizing images via an API.

    Provides a mechanism for processing input images to produce ranked image
    labels. Credentials are stored once in self._api_key at instance
    construction and are subclass specific in structure.
    """
    def __init__(self, api_key):
        self._api_key = api_key

    def fetch_labels(self, image_data, image_extension):
        """Retrieve a list of label, rank pairs from an API.

        Subclasses should override this as it is service specific.
        """
        raise NotImplementedError()

    def recognize(self, image_data, image_extension=None, threshold=0, max_labels=1):
        """Apply the image recognition service to the supplied image data and
        constraints.

        image_data -- a byte string representing the image in a common format.
        image_extension -- indicates the image format used. Note, this is not
            taken into account by all services.
        threshold -- any image labels ranked less than threshold will not be
            considered at all.
        max_labels -- the maximum number of image labels to return.

        returns -- a list of image labels sorted by rank descending.
        """
        image_labels = self.fetch_labels(image_data, image_extension)
        return self.select_image_labels(image_labels, threshold, max_labels)

    @staticmethod
    def select_image_labels(image_labels, threshold, max_labels):
        """Find a list of ImageLabels fitting the given constraints ordered
        by label rank.

        image_labels -- a list of ImageLabels to select from.
        threshold -- the minimum score at which a ImageLabel will be chosen.
        max_labels -- the maximum number of ImageLabels returned.

        returns -- a list of ImageLabels.
        """
        fit_image_labels = [label
                            for label in image_labels
                            if label.rank >= threshold]
        selected_image_labels = [
            image_label.label
            for image_label in sorted(fit_image_labels, key=lambda label: label.rank)
        ]
        return selected_image_labels[:min(len(selected_image_labels), max_labels)]


class CloudSight(ImageRecogonitionService):
    """An interface to the CloudSight image recognition service.

    Example:
        client_instance = CloudSight('XXXAPIKEYXXX')
        image_labels = client_instance.recognize(jpg_image_data, '.jpg')
    """
    def fetch_labels(self, image_data, image_extension):
        try:
            auth = cloudsight.SimpleAuth(self._api_key)
            api = cloudsight.API(auth)
            response = api.image_request(
                image_data,
                'image.{}'.format(image_extension),
                {'image_request[locale]': 'en-US'}
            )
            api.wait(response['token'], timeout=30)
            response = api.image_response(response['token'])
            status = response['status']
            if status == cloudsight.STATUS_COMPLETED:
                return [ImageLabel(label=response['name'], rank=1)]
            elif status == cloudsight.STATUS_SKIPPED:
                raise ImageRecognitionException(response['reason'])
            else:
                raise ImageRecognitionException('Service unavailable')
        except APIError:
            raise ImageRecognitionException('Service unavailable')


class GoogleVision(ImageRecogonitionService):
    """An interface to the Google Vision image recognition service.

    Note, image_extension is not meaningful here.

    Example:
        client_instance = GoogleVision('XXXAPIKEYXXX')
        image_labels = client_instance.recognize(image_data)
    """
    def fetch_labels(self, image_data, image_extension=None):
        try:
            client_instance = googlevision.Client(self._api_key)
            image = client_instance.image(content=image_data)
            labels = image.detect_labels()
            return [ImageLabel(label=label.description, rank=label.score) for label in labels]
        except GoogleCloudError:
            raise ImageRecognitionException('Service unavailable')


class Rekognition(ImageRecogonitionService):
    """An interface to the AWS Rekognition image recognition service.

    Note, image_extension is not meaningful here.

    Example:
        client_instance = Rekognition({
            'access_key_id': 'XXXACCESSKEYIDXXX',
            'secret_key': 'XXXSECRETKEYXXX',
        )
        image_labels = client_instance.recognize(image_data)
    """
    def fetch_labels(self, image_data, image_extension=None):
        try:
            client_instance = boto3.client(
                'rekognition',
                aws_access_key_id=self._api_key['access_key_id'],
                aws_secret_access_key=self._api_key['secret_key']
            )
            response = client_instance.detect_labels(Image={'Bytes': image_data})
            labels = response['Labels']
            return [
                # Rekognition ranks images on a scale of 0 to 100.
                ImageLabel(label=label['Name'], rank=label['Confidence']/100.0)
                for label in labels
            ]
        except ClientError as e:
            raise ImageRecognitionException('Service unavailable')
