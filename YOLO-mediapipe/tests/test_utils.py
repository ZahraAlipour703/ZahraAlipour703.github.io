"""
Unit tests for src.utils.utils helper functions.

Run with:
    pytest tests/test_utils.py
"""

import pytest

from src.utils.utils import bbox_center, clip_bbox, euclidean_distance, midpoint


def test_euclidean_distance():
    assert euclidean_distance((0, 0), (3, 4)) == pytest.approx(5.0)


def test_midpoint():
    assert midpoint((0, 0), (4, 6)) == (2, 3)


def test_bbox_center():
    # bbox = [x1, y1, x2, y2]
    assert bbox_center([0, 0, 10, 20]) == (5, 10)


def test_clip_bbox_within_bounds_is_unchanged():
    bbox = [10, 10, 50, 50]
    assert tuple(clip_bbox(bbox, width=100, height=100)) == (10, 10, 50, 50)


def test_clip_bbox_clips_to_frame():
    bbox = [-5, -5, 150, 150]
    clipped = clip_bbox(bbox, width=100, height=100)

    assert clipped[0] >= 0
    assert clipped[1] >= 0
    assert clipped[2] <= 100
    assert clipped[3] <= 100
