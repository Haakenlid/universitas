"""Tests of the cropping detectors."""

import json

import pytest

from apps.photo.cropping.boundingbox import Box, CropBox
from apps.photo.cropping.crop_detector import (
    Cascade,
    Feature,
    FeatureDetector,
    KeypointDetector,
    MockFeatureDetector,
)
from apps.photo.cropping.crop_engine import calculate_crop, close_crop


@pytest.fixture(params=FeatureDetector.__subclasses__())
def detector(request):
    Detector = request.param
    return Detector(n=10)


def test_crop_algorithm():
    # some basic cases
    cropbox = CropBox.basic().serialize()
    assert close_crop(**cropbox, aspect_ratio=1) == Box(0, 0, 1, 1)
    assert close_crop(**cropbox, aspect_ratio=2) == Box(0, 0.25, 1, 0.75)
    assert close_crop(**cropbox, aspect_ratio=0.5) == Box(0.25, 0, 0.75, 1)


def test_calculate_crop():
    # valid input
    kwargs = dict(width=200, height=100, crop_width=50, crop_height=50, exp=0)
    crop_box = CropBox(.2, .2, .8, .8, .6, .6)
    assert calculate_crop(
        crop_box=crop_box.serialize(), **kwargs
    ) == Box(60, 0, 160, 100)

    # invalid input (width is zero) causes fallback
    crop_box.width = 0
    assert calculate_crop(
        crop_box=crop_box.serialize(), **kwargs
    ) == Box(50, 0, 150, 100)


def test_cascade_loading():
    VALID_CASCADE = 'haarcascade_smile.xml'
    INVALID_CASCADE = 'no_such_cascade.xml'
    smile_cascade = Cascade('nose', VALID_CASCADE)
    assert not smile_cascade.classifier.empty()

    with pytest.raises(RuntimeError):
        Cascade('invalid', INVALID_CASCADE)


def test_cropdetector(detector, jpeg_file):
    features = detector.detect_features(jpeg_file)
    assert len(features) >= 1
    assert 0 < sum(features).size < 1
    keys = {'x', 'y', 'width', 'height', 'label', 'weight'}
    assert set(features[0].serialize().keys()) == keys


def test_serialize_and_deserialize():
    feature = Feature(5, 'hello', 1, 2, 4, 9)
    dump = json.dumps(feature.serialize())
    data = json.loads(dump)
    assert data == {
        "label": "hello", "x": 1, "y": 2, "width": 3, "height": 7, "weight": 5
    }
    clone = Feature.deserialize(data)
    assert clone == feature


def test_that_keypointdetector_returns_correct_number_of_features(jpeg_file):
    detector = KeypointDetector(n=5)
    features = detector.detect_features(jpeg_file)
    assert len(features) == 5


def test_that_both_file_and_bytes_work(jpeg_file):
    detector = MockFeatureDetector(n=3)
    data = jpeg_file.read_bytes()
    features = detector.detect_features(jpeg_file)
    features2 = detector.detect_features(data)
    assert len(features) == 3
    assert features == features2


def test_feature_operators():
    f1 = Feature(1, 'f1', 1, 2, 3, 4)
    f2 = Feature(2, 'f2', 2, 1, 4, 3)
    combined = f1 + f2
    assert combined == Box(1, 1, 4, 4)
    intersection = f1 & f2
    assert intersection == Box(2, 2, 3, 3)
    double = f1 * 2
    assert double == Feature(2, 'f1', 0, 1, 4, 5)
