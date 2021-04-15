"""Streams API Scan event model."""
from dataclasses import dataclass
from marshmallow import fields, validate

from proglove_streams.models.event import (
    StreamsAPIEventSchema,
    StreamsAPIEvent)
from proglove_streams.models.event_type import EventType


@dataclass
class ScanEvent(StreamsAPIEvent):
    """Streams API scanner state event model."""

    scan_code: str = ''
    device_serial: str = ''


class ScanEventSchema(StreamsAPIEventSchema):
    """Streams API scan event schema."""

    __model__ = ScanEvent

    event_type = fields.String(required=True,
                               validate=validate.Equal(EventType.SCAN.value))

    scan_code = fields.String(required=True,
                              validate=validate.Length(min=1, max=2000))

    device_serial = fields.String(required=True,
                                  validate=validate.Length(min=1, max=128))
