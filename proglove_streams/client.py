"""Streams API client."""
from typing import Protocol


# pylint: disable=too-few-public-methods
class Client(Protocol):
    """Streams API client.

    Used to connect to a serial device that understands the Streams API.

    """
