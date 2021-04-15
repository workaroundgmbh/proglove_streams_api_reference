"""Base model module."""
from dataclasses import dataclass
from typing import Any, Dict
from marshmallow import Schema, post_load, post_dump


@dataclass
class BaseModel:
    """Base model."""

    _dummy: str = ''


class BaseSchema(Schema):
    """Base schema."""

    __model__ = BaseModel

    @post_load
    def make_model(self, data: Dict[str, Any], **_kwargs):
        """Create a model from a dict."""
        return self.__model__(**data)

    # pylint: disable=no-self-use
    @post_dump()
    def dump_json(self, event: Dict[str, Any], **_kwargs):
        """Create a dict from the model."""
        for key, value in event.copy().items():
            if value is None:
                del event[key]

        return event
