"""Streams API button pressed event model."""
from dataclasses import dataclass
from marshmallow import fields, validate

from proglove_streams.models.event import (
    StreamsAPIEventSchema,
    StreamsAPIEvent)
from proglove_streams.models.event_type import EventType


@dataclass
class ButtonPressedEvent(StreamsAPIEvent):
    """Streams API button pressed event model."""

    device_serial: str = ''
    trigger_gesture: str = ''


class ButtonPressedSchema(StreamsAPIEventSchema):
    """Streams API button pressed schema."""

    __model__ = ButtonPressedEvent

    event_type = fields.String(required=True,
                               validate=validate.Equal(
                                   EventType.BUTTON_PRESSED.value))

    gateway_serial = fields.String(required=True,
                                   validate=validate.Length(min=1, max=128))

    device_serial = fields.String(required=True,
                                  validate=validate.Length(min=1, max=128))

    trigger_gesture = fields.String(
        validate=validate.OneOf([
            "TRIGGER_DOUBLE_CLICK",
        ]))
