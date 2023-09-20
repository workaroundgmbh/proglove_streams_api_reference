"""Gateway module."""
import json
import logging
import time
import uuid
from threading import Event, Thread
from typing import Any, Dict, List, Optional, Union

from serial import Serial, SerialException
from streams_api.customer_integrations.button_pressed.model import ButtonPressedStream
from streams_api.customer_integrations.errors.model import ErrorsStream
from streams_api.customer_integrations.gateway_state_event.model import (
    GatewayStateEventStream,
)
from streams_api.customer_integrations.handler import get_stream
from streams_api.customer_integrations.scan.model import ScanStream
from streams_api.customer_integrations.scanner_state.model import ScannerStateStream

from proglove_streams.client import Client
from proglove_streams.exception import ProgloveStreamsException
from proglove_streams.handler import Handler

logger = logging.getLogger(__name__)


# pylint: disable=too-few-public-methods
class GatewayMessageHandler(Handler):
    """Default Gateway message handler."""

    def handle(self, client: Client, event: Dict) -> None:
        """Handle the events."""
        logger.debug("event received: %s", event)

        if "event_type" not in event:
            logger.warning("event_type field not found")
            return

        event_type = event["event_type"]
        try:
            stream = get_stream(event)
        except ValueError:
            return

        if isinstance(stream, ScanStream):
            self._handle_scan(client, stream)
        elif isinstance(stream, ScannerStateStream):
            self._handle_scanner_state(client, stream)
        elif isinstance(stream, ErrorsStream):
            self._handle_error(client, stream)
        elif isinstance(stream, GatewayStateEventStream):
            self._handle_gateway_state(client, stream)
        elif isinstance(stream, ButtonPressedStream):
            self._handle_button_pressed(client, stream)
        else:
            logger.warning('could not find a handler for event "%s"', event_type)

    def _handle_button_pressed(
        self, client: Client, event: ButtonPressedStream
    ) -> None:
        """Handle a button pressed."""
        if self.on_button_pressed is not None:
            self.on_button_pressed(client, event)

    def _handle_scan(self, client: Client, event: ScanStream) -> None:
        """Handle a scan."""

        if self.on_scan is not None:
            self.on_scan(client, event)

    def _handle_scanner_state(self, client: Client, event: ScannerStateStream) -> None:
        """Handle a scanner state event."""

        if event.device_connected_state == "STATE_CONNECTED":
            if self.on_scanner_connected is not None:
                self.on_scanner_connected(client, event)
        else:
            if self.on_scanner_disconnected is not None:
                self.on_scanner_disconnected(client, event)

    def _handle_error(self, client: Client, event: ErrorsStream) -> None:
        """Handle an error event."""

        if self.on_error is not None:
            self.on_error(client, event)

    def _handle_gateway_state(
        self, client: Client, event: GatewayStateEventStream
    ) -> None:
        """Handle a Gateway state event."""
        if self.on_gateway_state_event is not None:
            self.on_gateway_state_event(client, event)


class Gateway:
    """Gateway class."""

    def __init__(self, handler: Handler, port: str, baudrate: int = 115200):
        """Initialize the class."""
        self._input_thread: Optional[Thread] = None
        self._is_running = Event()
        self._port = port
        self._baudrate = baudrate
        self._handler = handler

        self._serial: Optional[Serial] = None

    def start(self, flush_input: bool = True) -> None:
        """Start servicing the wrapped connection."""
        if self._is_running.is_set():
            return

        logger.info("start the Gateway client")

        if self._serial is not None:
            self._serial.close()
            self._serial = None

        try:
            logger.debug(
                "open serial port %s with baudrate %u", self._port, self._baudrate
            )
            self._serial = Serial(self._port, self._baudrate, timeout=0.1)

            if flush_input:
                for _ in range(10):
                    _ = self._serial.readall()

        except SerialException as e:
            logger.error("could not open serial connection: %s", e)
            raise ProgloveStreamsException(str(e)) from e

        logger.debug("start the input thread")
        self._input_thread = Thread(target=self._input_loop, daemon=True)
        self._input_thread.start()

        self._is_running.wait()
        logger.info("Gateway client started")

    def stop(self) -> None:
        """Stop the serial communication."""
        logger.info("stop the Gateway client")

        if self._input_thread is not None:
            logger.debug("stop the input thread")
            self._is_running.clear()
            self._input_thread.join()
            self._input_thread = None

        if self._serial is not None:
            logger.debug("close the serial connection")
            self._serial.close()
            self._serial = None

    def get_gateway_state(self) -> None:
        """Get the Gateway state command."""
        logger.info("Get Gateway state")

        command = {
            "api_version": "1.0",
            "event_type": "gateway_state!",
            "event_id": str(uuid.uuid4()),
            "time_created": int(time.time() * 1000),
        }

        self._send_command(command)

    def send_feedback(self, device_serial: str, feedback_action_id: str) -> None:
        """Send a feedback command.

        Arguments:
            device_serial: The Mark serial number.
            feedback_action_id: The action ID of the feedback.

        """
        logger.info("Send a feedback command")

        command = {
            "api_version": "1.0",
            "event_type": "feedback!",
            "event_id": str(uuid.uuid4()),
            "time_created": int(time.time() * 1000),
            "device_serial": device_serial,
            "feedback_action_id": feedback_action_id,
        }

        self._send_command(command)

    # pylint: disable=too-many-arguments disable=duplicate-code
    def set_display(
        self,
        device_serial: str,
        display_template_id: str,
        display_fields: List[Dict[str, Union[int, str]]],
        display_refresh_type: str = "DEFAULT",
        time_validity_duration: Optional[int] = None,
    ) -> None:
        """Send a display command.

        Arguments:
            device_serial: The Mark serial number.
            display_template_id: The template ID to display.
            display_fields: A list of fields to display.
            display_refresh_type: The display refresh type.
            time_validity_duration: The time the display should be shown.

        """
        logger.info("Send a Display command")

        command = {
            "api_version": "1.0",
            "event_type": "display!",
            "event_id": str(uuid.uuid4()),
            "time_created": int(time.time() * 1000),
            "device_serial": device_serial,
            "display_template_id": display_template_id,
            "display_refresh_type": display_refresh_type,
            "display_fields": display_fields,
        }

        if time_validity_duration is not None:
            command["time_validity_duration"] = time_validity_duration

        self._send_command(command)

    # pylint: disable=too-many-arguments disable=duplicate-code
    def set_trigger_block(
        self,
        device_serial: str,
        trigger_block_state: bool,
        trigger_block_gesture_list: List[str],
        trigger_unblock_gesture_list: List[str],
        time_validity_duration: Optional[int] = None,
    ) -> None:
        """Send a trigger block command.

        Arguments:
            device_serial: The Mark serial number.
            trigger_block_state: The state of the trigger block.
            trigger_block_gesture_list: A list of triggers to block.
            trigger_unblock_gesture_list: A list of trigger that can ublock.
            time_validity_duration: The time the blocking should last.

        """
        logger.info("Send a trigger block command")

        command = {
            "api_version": "1.0",
            "event_type": "trigger_block!",
            "event_id": str(uuid.uuid4()),
            "time_created": int(time.time() * 1000),
            "device_serial": device_serial,
            "trigger_block_gesture_list": trigger_block_gesture_list,
            "trigger_unblock_gesture_list": trigger_unblock_gesture_list,
            "trigger_block_state": trigger_block_state,
        }

        if time_validity_duration is not None:
            command["time_validity_duration"] = time_validity_duration

        self._send_command(command)

    def _input_loop(self) -> None:
        self._is_running.set()

        while self._is_running.is_set():
            if self._serial is None:
                self._is_running.clear()
                return

            try:
                line = self._serial.readline()
            except SerialException as e:
                logger.error("could not read from serial: %s", e)
                self._is_running.clear()
                return

            if not line:
                continue
            try:
                event = json.loads(line.strip())
                self._handler.handle(self, event)
            except json.decoder.JSONDecodeError as e:
                logger.debug("malformed JSON: %s", e)

    def _send_command(self, command: Dict[str, Any]) -> None:
        if self._serial is None:
            logger.warning("serial connection not opened")
            raise ProgloveStreamsException("serial connection not opened")

        logger.debug("send command %s", command)
        try:
            self._serial.write(json.dumps(command).encode())
            self._serial.write(b"\n")
        except SerialException as e:
            logger.error("could not send data to serial: %s", e)
            raise ProgloveStreamsException(str(e)) from e

    def __enter__(self) -> "Gateway":
        """Use context manager."""
        self.start()
        return self

    def __exit__(self, _exc_type: Any, _exc_val: Any, _exc_tb: Any) -> None:
        """Close context manager."""
        self.stop()
