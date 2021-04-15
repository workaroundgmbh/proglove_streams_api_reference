"""Test for the logging module."""
from unittest.mock import patch


from proglove_streams.logging import init_logging


def test_logging():
    """Test the logging functionality."""
    with patch('proglove_streams.logging.logging.StreamHandler'):
        init_logging()
