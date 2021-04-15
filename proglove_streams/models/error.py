"""Streams API error event model."""
from typing import Optional
from dataclasses import dataclass
from marshmallow import fields, validate

from proglove_streams.models.event import (
    StreamsAPIEventSchema,
    StreamsAPIEvent)
from proglove_streams.models.event_type import EventType


@dataclass
class ErrorEvent(StreamsAPIEvent):
    """Streams API scanner state event model."""

    error_code: str = ''
    event_reference_id: Optional[str] = None
    error_severity: Optional[str] = None
    error_message: Optional[str] = None
    device_serial: Optional[str] = None


class ErrorEventSchema(StreamsAPIEventSchema):
    """Streams API error event schema."""

    __model__ = ErrorEvent

    event_type = fields.String(required=True,
                               validate=validate.Equal(EventType.ERROR.value))

    event_reference_id = fields.String(validate=validate.Regexp(
        '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'))

    error_severity = fields.String(
        validate=validate.OneOf([
            "WARNING",
            "ERROR",
            "CRITICAL"
        ]))

    error_message = fields.String(valids=validate.Range(min=1, max=128))

    error_code = fields.String(
        validate=validate.OneOf([
            "ERROR_UNKNOWN",
            "ERROR_OK",
            "ERROR_INVALID_COMMAND",
            "ERROR_TIMEOUT",
            "ERROR_DEVICE_NOT_FOUND"
        ]))

    device_serial = fields.String(validate=validate.Length(min=1, max=128))
