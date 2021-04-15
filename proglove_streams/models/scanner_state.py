"""Streams API Scanner state event model."""
from typing import Optional
from dataclasses import dataclass
from marshmallow import fields, validate

from proglove_streams.models.event import (
    StreamsAPIEventSchema,
    StreamsAPIEvent
)
from proglove_streams.models.event_type import EventType


@dataclass
class ScannerStateEvent(StreamsAPIEvent):
    """Streams API scanner state event model."""

    device_connected_state: str = 'STATE_DISCONNECTED'
    device_serial: str = ''
    device_disconnect_reason: Optional[str] = None


class ScannerStateEventSchema(StreamsAPIEventSchema):
    """Streams API scanner state event schema."""

    __model__ = ScannerStateEvent

    event_type = fields.String(
        required=True,
        validate=validate.Equal(EventType.SCANNER_STATE.value))

    device_connected_state = fields.String(required=True,
                                           validate=validate.OneOf([
                                               "STATE_CONNECTED",
                                               "STATE_DISCONNECTED"
                                           ]))

    device_serial = fields.String(required=True,
                                  validate=validate.Length(min=1, max=128))

    device_disconnect_reason = fields.String(
        validate=validate.OneOf(["UNKNOWN"]))
