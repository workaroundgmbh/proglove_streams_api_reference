"""Base Streams API event module."""
from dataclasses import dataclass
from typing import Optional
from marshmallow import fields, validate

from proglove_streams.models.base import BaseSchema
from proglove_streams.models.base import BaseModel


@dataclass
class StreamsAPIEvent(BaseModel):
    """Base Streams API event model."""

    api_version: str = ''
    event_type: str = ''
    event_id: str = ''
    time_created: int = 0
    gateway_serial: Optional[str] = None


class StreamsAPIEventSchema(BaseSchema):
    """Base Streams API event schema."""

    __model__ = StreamsAPIEvent

    api_version = fields.String(required=True, validate=validate.Equal('1.0'))

    event_type = fields.String(required=True)

    event_id = fields.String(required=True, validate=validate.Regexp(
        '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'))

    time_created = fields.Integer(required=True,
                                  validate=validate.Range(min=1546300800000,
                                                          max=99999999999999))

    gateway_serial = fields.String(validate=validate.Length(min=1, max=128))
