"""Shared test fixtures."""

import sys
import os
import pytest

# Ensure backend is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import msgpack
from starlette.testclient import TestClient

from backend.app import app as fastapi_app


@pytest.fixture
def client():
    """Synchronous test client using Starlette's TestClient."""
    with TestClient(fastapi_app) as c:
        yield c


def msgpack_post(client, url, data):
    """Helper to POST msgpack-encoded data and decode the response."""
    body = msgpack.packb(data, use_bin_type=True)
    response = client.post(url, content=body, headers={'Content-Type': 'application/x-msgpack'})
    return response, msgpack.unpackb(response.content, raw=False)


def msgpack_get(client, url):
    """Helper to GET and decode a msgpack response."""
    response = client.get(url)
    return response, msgpack.unpackb(response.content, raw=False)
