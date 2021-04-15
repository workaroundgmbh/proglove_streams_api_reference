"""Streams API Gateway state event model."""
from typing import Optional, List
from dataclasses import dataclass, field
from marshmallow import fields, validate

from proglove_streams.models.event import (
    StreamsAPIEventSchema,
    StreamsAPIEvent)
from proglove_streams.models.base import BaseSchema, BaseModel
from proglove_streams.models.event_type import EventType


@dataclass
class GatewayStateDeviceConnectedEvent(BaseModel):
    """Streams API Gateway state device connected object."""

    device_serial: str = ''
    device_firmware_version: Optional[str] = None
    device_model: Optional[str] = None
    device_manufacturer: Optional[str] = None


class GatewayStateDeviceConnectedEventSchema(BaseSchema):
    """Streams API Gateway state device connected schema."""

    __model__ = GatewayStateDeviceConnectedEvent

    device_serial = fields.String(required=True,
                                  validate=validate.Length(min=1, max=128))

    device_firmware_version = fields.String(
        validate=validate.Length(min=1, max=128))

    device_model = fields.String(validate=validate.Length(min=1, max=128))

    device_manufacturer = fields.String(
        validate=validate.Length(min=1, max=128))


@dataclass
class GatewayStateEvent(StreamsAPIEvent):
    """Streams API Gateway state event model."""

    gateway_app_version: str = ''
    device_connected_list: List[GatewayStateDeviceConnectedEvent] = field(
        default_factory=list)
    event_reference_id: Optional[str] = None


class GatewayStateEventSchema(StreamsAPIEventSchema):
    """Streams API Gateway state event schema."""

    __model__ = GatewayStateEvent

    event_type = fields.String(required=True,
                               validate=validate.Equal(
                                   EventType.GATEWAY_STATE.value))

    gateway_serial = fields.String(required=True,
                                   validate=validate.Length(min=1, max=128))

    event_reference_id = fields.String(validate=validate.Regexp(
        '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'))

    gateway_app_version = fields.String(
        required=True, validate=validate.Length(min=1, max=128))

    device_connected_list = fields.List(
        fields.Nested(GatewayStateDeviceConnectedEventSchema),
        validate=validate.Length(max=50))
