"""Gateway module."""
import json
import logging
import time
import uuid
from threading import Thread, Event
from typing import Any, Dict, List, Optional, Union

from serial import Serial, SerialException
from marshmallow.validate import ValidationError

from proglove_streams.models.error import (
    ErrorEventSchema,
    ErrorEvent
)
from proglove_streams.models.gateway_state import (
    GatewayStateEvent,
    GatewayStateEventSchema
)
from proglove_streams.models.scan import (
    ScanEventSchema,
    ScanEvent
)
from proglove_streams.models.scanner_state import (
    ScannerStateEventSchema,
    ScannerStateEvent
)
from proglove_streams.models.button_pressed import (
    ButtonPressedSchema,
    ButtonPressedEvent
)
from proglove_streams.models.event_type import EventType
from proglove_streams.handler import Handler
from proglove_streams.client import Client

from proglove_streams.exception import ProgloveStreamsException


logger = logging.getLogger(__name__)


# pylint: disable=too-few-public-methods
class GatewayMessageHandler(Handler):
    """Default Gateway message handler."""

    def handle(self, client: Client, event: Dict):
        """Handle the events."""
        logger.debug('event received: %s', event)

        if 'event_type' not in event:
            logger.warning('event_type field not found')
            return

        event_type = event['event_type']

        if event_type == EventType.SCAN.value:
            self._handle_scan(client, event)
        elif event_type == EventType.SCANNER_STATE.value:
            self._handle_scanner_state(client, event)
        elif event_type == EventType.ERROR.value:
            self._handle_error(client, event)
        elif event_type == EventType.GATEWAY_STATE.value:
            self._handle_gateway_state(client, event)
        elif event_type == EventType.BUTTON_PRESSED.value:
            self._handle_button_pressed(client, event)
        else:
            logger.warning('could not find a handler for event "%s"',
                           event_type)

    def _handle_button_pressed(self, client: Client, event: Dict):
        """Handle a button pressed."""
        try:
            button_press_event: ButtonPressedEvent = (
                ButtonPressedSchema().load(event))
        except ValidationError as e:
            logger.warning('could not validate event: %s', e)
            return

        if self.on_button_pressed is not None:
            self.on_button_pressed(client, button_press_event)

    def _handle_scan(self, client: Client, event: Dict):
        """Handle a scan."""
        try:
            scan_event: ScanEvent = ScanEventSchema().load(event)
        except ValidationError as e:
            logger.warning('could not validate event: %s', e)
            return

        if self.on_scan is not None:
            self.on_scan(client, scan_event)

    def _handle_scanner_state(self, client: Client, event: Dict[str, Any]):
        """Handle a scanner state event."""
        try:
            device_state: ScannerStateEvent = (
                ScannerStateEventSchema().load(event))
        except ValidationError as e:
            logger.warning('could not validate event: %s', e)
            return

        if device_state.device_connected_state == 'STATE_CONNECTED':
            if self.on_scanner_connected is not None:
                self.on_scanner_connected(client, device_state)
        else:
            if self.on_scanner_disconnected is not None:
                self.on_scanner_disconnected(client, device_state)

    def _handle_error(self, client: Client, event: Dict):
        """Handle an error event."""
        try:
            error_event: ErrorEvent = ErrorEventSchema().load(event)
        except ValidationError as e:
            logger.warning('could not validate event: %s', e)
            return

        if self.on_error is not None:
            self.on_error(client, error_event)

    def _handle_gateway_state(self, client: Client, event: Dict):
        """Handle a Gateway state event."""
        try:
            gateway_state_event: GatewayStateEvent = (
                GatewayStateEventSchema().load(event))
        except ValidationError as e:
            logger.warning('could not validate event: %s', e)
            return

        if self.on_gateway_state_event is not None:
            self.on_gateway_state_event(client, gateway_state_event)


class Gateway:
    """Gateway class."""

    def __init__(self,
                 handler: Handler,
                 port: str,
                 baudrate: int = 115200):
        """Initialize the class."""
        self._input_thread: Optional[Thread] = None
        self._is_running = Event()
        self._port = port
        self._baudrate = baudrate
        self._handler = handler

        self._serial: Optional[Serial] = None

    def start(self, flush_input: bool = True):
        """Start servicing the wrapped connection."""
        if self._is_running.is_set():
            return

        logger.info('start the Gateway client')

        if self._serial is not None:
            self._serial.close()
            self._serial = None

        try:
            logger.debug('open serial port %s with baudrate %u',
                         self._port, self._baudrate)
            self._serial = Serial(self._port, self._baudrate, timeout=0.1)

            if flush_input:
                for _ in range(10):
                    _ = self._serial.readall()

        except SerialException as e:
            logger.error('could not open serial connection: %s',  e)
            raise ProgloveStreamsException(str(e)) from e

        logger.debug('start the input thread')
        self._input_thread = Thread(target=self._input_loop,
                                    daemon=True)
        self._input_thread.start()

        self._is_running.wait()
        logger.info('Gateway client started')

    def stop(self):
        """Stop the serial communication."""
        logger.info('stop the Gateway client')

        if self._input_thread is not None:
            logger.debug('stop the input thread')
            self._is_running.clear()
            self._input_thread.join()
            self._input_thread = None

        if self._serial is not None:
            logger.debug('close the serial connection')
            self._serial.close()
            self._serial = None

    def get_gateway_state(self):
        """Get the Gateway state command."""
        logger.info('Get Gateway state')

        command = {
            "api_version": "1.0",
            "event_type": 'gateway_state!',
            "event_id": str(uuid.uuid4()),
            "time_created": int(time.time() * 1000)
        }

        self._send_command(command)

    def send_feedback(self,
                      device_serial: str,
                      feedback_action_id: str):
        """Send a feedback command.

        Arguments:
            device_serial: The Mark serial number.
            feedback_action_id: The action ID of the feedback.

        """
        logger.info('Send a feedback command')

        command = {
            "api_version": "1.0",
            "event_type": 'feedback!',
            "event_id": str(uuid.uuid4()),
            "time_created": int(time.time() * 1000),
            "device_serial": device_serial,
            'feedback_action_id': feedback_action_id,
        }

        self._send_command(command)

    # pylint: disable=too-many-arguments disable=duplicate-code
    def set_display(self,
                    device_serial: str,
                    display_template_id: str,
                    display_fields: List[Union[Dict[str, Union[int, str]]]],
                    display_refresh_type: str = 'DEFAULT',
                    time_validity_duration: Optional[int] = None) -> None:
        """Send a display command.

        Arguments:
            device_serial: The Mark serial number.
            display_template_id: The template ID to display.
            display_fields: A list of fields to display.
            display_refresh_type: The display refresh type.
            time_validity_duration: The time the display should be shown.

        """
        logger.info('Send a Display command')

        command = {
            "api_version": "1.0",
            "event_type": 'display!',
            "event_id": str(uuid.uuid4()),
            "time_created": int(time.time() * 1000),
            "device_serial": device_serial,
            'display_template_id': display_template_id,
            'display_refresh_type': display_refresh_type,
            "display_fields": display_fields,
        }

        if time_validity_duration is not None:
            command['time_validity_duration'] = time_validity_duration

        self._send_command(command)

    # pylint: disable=too-many-arguments disable=duplicate-code
    def set_trigger_block(self,
                          device_serial: str,
                          trigger_block_state: bool,
                          trigger_block_gesture_list: List[str],
                          trigger_unblock_gesture_list: List[str],
                          time_validity_duration: Optional[int] = None
                          ) -> None:
        """Send a trigger block command.

        Arguments:
            device_serial: The Mark serial number.
            trigger_block_state: The state of the trigger block.
            trigger_block_gesture_list: A list of triggers to block.
            trigger_unblock_gesture_list: A list of trigger that can ublock.
            time_validity_duration: The time the blocking should last.

        """
        logger.info('Send a trigger block command')

        command = {
            "api_version": "1.0",
            "event_type": 'trigger_block!',
            "event_id": str(uuid.uuid4()),
            "time_created": int(time.time() * 1000),
            "device_serial": device_serial,
            'trigger_block_gesture_list': trigger_block_gesture_list,
            'trigger_unblock_gesture_list': trigger_unblock_gesture_list,
            "trigger_block_state": trigger_block_state,
        }

        if time_validity_duration is not None:
            command['time_validity_duration'] = time_validity_duration

        self._send_command(command)

    def _input_loop(self):
        self._is_running.set()

        while self._is_running.is_set():
            if self._serial is None:
                self._is_running.clear()
                return

            try:
                line = self._serial.readline()
            except SerialException as e:
                logger.error('could not read from serial: %s', e)
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
            logger.warning('serial connection not opened')
            raise ProgloveStreamsException('serial connection not opened')

        logger.debug('send command %s', command)
        try:
            self._serial.write(json.dumps(command).encode())
            self._serial.write(b'\n')
        except SerialException as e:
            logger.error('could not send data to serial: %s', e)
            raise ProgloveStreamsException(str(e)) from e

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, _exc_type, _exc_val, _exc_tb):
        self.stop()
