"""Test for the Gateway module."""
import json
import logging
import os
import pty
import time
import uuid
from threading import Event
from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest
from pydantic import BaseModel
from streams_api.customer_integrations.button_pressed.model import ButtonPressedStream
from streams_api.customer_integrations.errors.model import ErrorsStream
from streams_api.customer_integrations.gateway_state_event.model import (
    DeviceConnectedListItem,
    GatewayStateEventStream,
)
from streams_api.customer_integrations.scan.model import DeviceModel, ScanStream
from streams_api.customer_integrations.scanner_state.model import ScannerStateStream

from proglove_streams.exception import ProgloveStreamsException
from proglove_streams.gateway import Gateway, GatewayMessageHandler

logger = logging.getLogger(__name__)


# pylint: disable=too-few-public-methods
class _SideEffect:
    def __init__(self, event: Event):
        self.event = event

    def side_effect(self, *_args, **_kwargs):
        """Side effect to call."""
        self.event.set()


@pytest.mark.parametrize(
    "model, callback_name, use_mock",
    [
        pytest.param(args[0], args[1], use_mock, id=args[2])
        for use_mock in (True, False)
        for args in (
            (
                ButtonPressedStream(
                    api_version="1.0",
                    event_id=str(uuid.uuid4()),
                    time_created=int(time.time() * 1000),
                    gateway_serial="PGGW000000042",
                    device_serial="123456789",
                    trigger_gesture="TRIGGER_DOUBLE_CLICK",
                ),
                "on_button_pressed",
                "button_pressed",
            ),
            (
                GatewayStateEventStream(
                    api_version="1.0",
                    event_id=str(uuid.uuid4()),
                    time_created=int(time.time() * 1000),
                    gateway_app_version="1.2.3",
                    gateway_serial="PGGW000000042",
                    device_connected_list=[
                        DeviceConnectedListItem(device_serial="M2MR111100928")
                    ],
                ),
                "on_gateway_state_event",
                "gateway_state",
            ),
            (
                ErrorsStream(
                    api_version="1.0",
                    event_id=str(uuid.uuid4()),
                    time_created=int(time.time() * 1000),
                    gateway_serial="PGGW000000042",
                    device_serial="123456789",
                    error_code="ERROR_UNKNOWN",
                    event_reference_id=str(uuid.uuid4()),
                    error_severity="CRITICAL",
                ),
                "on_error",
                "error",
            ),
            (
                ScannerStateStream(
                    api_version="1.0",
                    event_id=str(uuid.uuid4()),
                    time_created=int(time.time() * 1000),
                    gateway_serial="PGGW000000042",
                    device_serial="123456789",
                    device_connected_state="STATE_CONNECTED",
                ),
                "on_scanner_connected",
                "scanner_connected",
            ),
            (
                ScannerStateStream(
                    api_version="1.0",
                    event_id=str(uuid.uuid4()),
                    time_created=int(time.time() * 1000),
                    gateway_serial="PGGW000000042",
                    device_serial="123456789",
                    device_connected_state="STATE_DISCONNECTED",
                ),
                "on_scanner_disconnected",
                "scanner_disconnected",
            ),
            (
                ScanStream(
                    api_version="1.0",
                    event_id=str(uuid.uuid4()),
                    time_created=int(time.time() * 1000),
                    gateway_serial="PGGW000000042",
                    device_serial="123456789",
                    device_model=DeviceModel.m2_mr,
                    scan_code="foo bar baz",
                ),
                "on_scan",
                "scan",
            ),
        )
    ],
)
def test_events(
    model: BaseModel,
    callback_name: str,
    use_mock: bool,
):
    """Test all events."""
    master, slave = pty.openpty()
    slave_name = os.ttyname(slave)

    handler = GatewayMessageHandler()
    testee = Gateway(handler, port=slave_name)

    testee.start(flush_input=False)

    json_dict = model.json(exclude_none=True)

    event = Event()
    if use_mock:
        side_effect = _SideEffect(event)
        callback_mock = Mock(side_effect=side_effect.side_effect)
        setattr(handler, callback_name, callback_mock)

    os.write(master, json_dict.encode())
    event.wait(timeout=0.1)

    testee.stop()

    if use_mock:
        callback_mock.assert_called_with(testee, model)


@pytest.mark.parametrize(
    "wrong_dict, use_mock",
    [
        pytest.param(
            args[0],
            use_mock,  # pylint: disable=undefined-variable
            # pylint: disable=undefined-variable
            id=args[1] + "_%s" % ("mock" if use_mock else "no_mock"),
        )
        for args in (
            ({"foo": "bar"}, "no_event"),
            ({"event_type": "foo"}, "wrong_event"),
            ({"event_type": "button_pressed"}, "wrong_button_pressed"),
            ({"event_type": "scan"}, "wrong_scan"),
            ({"event_type": "scanner_state"}, "wrong_scanner_state"),
            ({"event_type": "errors", "foo": "bar"}, "wrong_error"),
            ({"event_type": "gateway_state"}, "wrong_gateway_state"),
        )
        for use_mock in (True, False)
    ],
)
def test_wrong_event(wrong_dict: Dict[str, Any], use_mock: bool):
    """Test wrong event."""
    master, slave = pty.openpty()
    slave_name = os.ttyname(slave)

    handler = GatewayMessageHandler()
    if use_mock:
        for field in handler.__dict__.copy():
            if field.startswith("on_"):
                setattr(handler, field, Mock())

    testee = Gateway(handler, port=slave_name)

    testee.start(flush_input=False)

    json_dict = json.dumps(wrong_dict)
    os.write(master, json_dict.encode())
    time.sleep(0.1)

    testee.stop()

    if use_mock:
        for field in handler.__dict__:
            if field.startswith("on_"):
                mock_fun: Mock = getattr(handler, field)
                mock_fun.assert_not_called()


@pytest.mark.parametrize(
    "function_name, event_type, args, kwargs, expected_fields",
    [
        pytest.param(
            "send_feedback",
            "feedback!",
            (
                "12345",
                "FOO",
            ),
            {},
            {
                "device_serial": "12345",
                "feedback_action_id": "FOO",
            },
            id="send_feedback",
        ),
        pytest.param(
            "set_display",
            "display!",
            (
                "12345",
                "FOOBAR",
                [
                    {
                        "display_field_id": 42,
                        "display_field_header": "Just a test",
                        "display_field_text": "R15",
                    },
                ],
            ),
            {
                "display_refresh_type": "ABCDEF",
                "time_validity_duration": 1234,
            },
            {
                "device_serial": "12345",
                "display_template_id": "FOOBAR",
                "display_refresh_type": "ABCDEF",
                "display_fields": [
                    {
                        "display_field_id": 42,
                        "display_field_header": "Just a test",
                        "display_field_text": "R15",
                    },
                ],
                "time_validity_duration": 1234,
            },
            id="set_display",
        ),
        pytest.param(
            "set_display",
            "display!",
            (
                "12345",
                "FOOBAR",
                [
                    {
                        "display_field_id": 42,
                        "display_field_header": "Just a test",
                        "display_field_text": "R15",
                    },
                ],
            ),
            {
                "display_refresh_type": "ABCDEF",
            },
            {
                "device_serial": "12345",
                "display_template_id": "FOOBAR",
                "display_refresh_type": "ABCDEF",
                "display_fields": [
                    {
                        "display_field_id": 42,
                        "display_field_header": "Just a test",
                        "display_field_text": "R15",
                    },
                ],
            },
            id="set_display_infinite",
        ),
        pytest.param(
            "set_trigger_block",
            "trigger_block!",
            ("12345", True, ["A", "B", "C"], ["D", "E", "F"]),
            {
                "time_validity_duration": 1234,
            },
            {
                "device_serial": "12345",
                "trigger_block_gesture_list": ["A", "B", "C"],
                "trigger_unblock_gesture_list": ["D", "E", "F"],
                "trigger_block_state": True,
                "time_validity_duration": 1234,
            },
            id="set_trigger_block",
        ),
        pytest.param(
            "set_trigger_block",
            "trigger_block!",
            ("12345", True, ["A", "B", "C"], ["D", "E", "F"]),
            {},
            {
                "device_serial": "12345",
                "trigger_block_gesture_list": ["A", "B", "C"],
                "trigger_unblock_gesture_list": ["D", "E", "F"],
                "trigger_block_state": True,
            },
            id="set_trigger_block_infinite",
        ),
        pytest.param(
            "get_gateway_state", "gateway_state!", (), {}, {}, id="get_gateway_state"
        ),
    ],
)
# pylint: disable=too-many-locals
def test_commands(
    function_name: str,
    event_type: str,
    args: Any,
    kwargs: Dict[str, Any],
    expected_fields: Dict[str, Any],
):
    """Test all commands."""
    master, slave = pty.openpty()
    slave_name = os.ttyname(slave)

    handler = GatewayMessageHandler()

    testee = Gateway(handler, port=slave_name)

    testee.start(flush_input=False)

    with patch("proglove_streams.gateway.time.time") as time_patch, patch(
        "proglove_streams.gateway.uuid.uuid4"
    ) as uuid4_patch:
        time_created = 1546300800000
        event_id = "c6fd7137-055a-4feb-8c32-9dbb9a117f6a"
        time_patch.return_value = time_created / 1000.0
        uuid4_patch.return_value = event_id
        getattr(testee, function_name)(*args, **kwargs)

        expected_dict = {
            "api_version": "1.0",
            "event_type": event_type,
            "event_id": event_id,
            "time_created": time_created,
        }

        expected_dict.update(expected_fields)
        json_expected_dict = json.dumps(expected_dict)

        data_read = os.read(master, len(json_expected_dict)).decode()
        assert data_read == json_expected_dict


def test_exceptions():
    """Test the exceptions."""
    testee = Gateway(Mock(), port="port_that_does_not_exist")

    with pytest.raises(ProgloveStreamsException):
        testee.start(flush_input=False)


def test_double_start():
    """Test client double start."""
    _, slave = pty.openpty()
    slave_name = os.ttyname(slave)

    handler = GatewayMessageHandler()

    with Gateway(handler, port=slave_name) as testee:
        testee.start(flush_input=False)


def test_thread_error():
    """Test error in the receiving thread."""
    _, slave = pty.openpty()
    slave_name = os.ttyname(slave)

    handler = GatewayMessageHandler()
    testee = Gateway(handler, port=slave_name)
    testee.start(flush_input=False)
    # pylint: disable=protected-access
    testee._serial.close()
    # pylint: disable=protected-access
    with pytest.raises(ProgloveStreamsException):
        testee._input_thread.join(timeout=1)
        testee.get_gateway_state()

    testee.start(flush_input=False)
    # pylint: disable=protected-access
    testee._serial = None
    # pylint: disable=protected-access
    testee._input_thread.join(timeout=1)
    with pytest.raises(ProgloveStreamsException):
        testee.get_gateway_state()

    testee.start(flush_input=False)
    # pylint: disable=protected-access
    testee._serial = None
    # pylint: disable=protected-access
    testee._input_thread.join(timeout=1)
    # pylint: disable=protected-access
    testee._input_thread = None
    testee.stop()


def test_malformed_json():
    """Test malformed JSON."""
    master, slave = pty.openpty()
    slave_name = os.ttyname(slave)

    handler = GatewayMessageHandler()
    testee = Gateway(handler, port=slave_name)

    testee.start(flush_input=False)

    os.write(master, b"{")

    testee.stop()
