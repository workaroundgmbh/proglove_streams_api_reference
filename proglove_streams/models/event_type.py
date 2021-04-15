"""Streams API event type module."""
from enum import Enum


class EventType(Enum):
    """Streams API event type."""
    DISPLAY = 'display!'
    ERROR = 'errors'
    FEEDBACK = 'feedback!'
    SCAN = 'scan'
    SCANNER_STATE = 'scanner_state'
    TRIGGER_BLOCK = 'trigger_block!'
    GATEWAY_STATE = 'gateway_state'
    BUTTON_PRESSED = 'button_pressed'
