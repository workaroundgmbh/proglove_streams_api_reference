"""Minimal example dumping whatever event it receives."""
import argparse
import logging
import platform
import time

from streams_api.customer_integrations.button_pressed.model import ButtonPressedStream
from streams_api.customer_integrations.errors.model import ErrorsStream
from streams_api.customer_integrations.gateway_state_event.model import (
    GatewayStateEventStream,
)
from streams_api.customer_integrations.scan.model import ScanStream
from streams_api.customer_integrations.scanner_state.model import ScannerStateStream

from proglove_streams.client import Client
from proglove_streams.exception import ProgloveStreamsException
from proglove_streams.gateway import Gateway, GatewayMessageHandler
from proglove_streams.logging import init_logging

logger = logging.getLogger(__name__)


def _set_display(client: Gateway, event: ScanStream) -> None:
    client.set_display(
        str(event.device_serial),
        "PG3",
        display_fields=[
            {
                "display_field_id": 1,
                "display_field_header": "Storage Unit",
                "display_field_text": "R15",
            },
            {
                "display_field_id": 2,
                "display_field_header": "Item",
                "display_field_text": "Engine 12",
            },
            {
                "display_field_id": 3,
                "display_field_header": "Quantity",
                "display_field_text": "10",
            },
        ],
    )


def _block_trigger(client: Gateway, event: ScanStream) -> None:
    client.set_trigger_block(
        str(event.device_serial),
        True,
        ["TRIGGER_SINGLE_CLICK"],
        [],
        time_validity_duration=3000,
    )


def _unblock_trigger(client: Gateway, event: ScanStream) -> None:
    client.set_trigger_block(str(event.device_serial), False, [], [])


def on_connected(_client: Client, event: ScannerStateStream) -> None:
    """On connected event callback."""
    logger.info("device connected: %s", event.device_serial)


def on_disconnected(_client: Client, event: ScannerStateStream) -> None:
    """On disconnected event callback."""
    logger.info("device disconnected: %s", event.device_serial)


def on_scan(client: Client, event: ScanStream) -> None:
    """On scan event callback."""
    if not isinstance(client, Gateway):
        return

    logger.info(
        "scan received: device %s, data: %s", event.device_serial, repr(event.scan_code)
    )

    scan_code = str(event.scan_code).split("\r")[0]

    if scan_code == "DISPLAY":
        _set_display(client, event)
    elif scan_code == "BLOCK":
        _block_trigger(client, event)
    elif scan_code == "UNBLOCK":
        _unblock_trigger(client, event)
    elif scan_code == "FEEDBACK_OK":
        client.send_feedback(str(event.device_serial), "FEEDBACK_POSITIVE")
    elif scan_code == "FEEDBACK_NOK":
        client.send_feedback(str(event.device_serial), "FEEDBACK_NEGATIVE")
    elif scan_code == "STATE":
        client.get_gateway_state()


def on_error(_client: Client, event: ErrorsStream) -> None:
    """On error event callback."""
    logger.info("error received: %s", event.error_code)


def on_gateway_state_event(_client: Client, event: GatewayStateEventStream) -> None:
    """On Gateway state event callback."""
    logger.info(
        """Gateway state received: serial: %s version: %s
                   connected devices: %s""",
        event.gateway_serial,
        event.gateway_app_version,
        ",".join([d.device_serial for d in event.device_connected_list]),
    )


def on_button_pressed_event(
    _client: Client,
    event: ButtonPressedStream,
) -> None:
    """On error event callback."""
    logger.info(
        "button pressed: device %s, trigger gesture: %s",
        event.device_serial,
        event.trigger_gesture,
    )


def app_example() -> None:
    """Run example of Streams API usage."""
    parser = argparse.ArgumentParser("proglove_streams")

    parser.add_argument(
        "-L",
        "--logging-level",
        help="set the logging level (default is DEBUG)",
        type=str,
        metavar="LEVEL",
        choices=("DEBUG", "INFO", "WARNING", "ERROR"),
        default="DEBUG",
    )
    parser.add_argument(
        "-b",
        "--baudrate",
        help="use a specific baudarate (default is  115200)",
        type=int,
        metavar="VALUE",
        default=115200,
    )
    parser.add_argument(
        "-p",
        "--port",
        help="path to the serial device port (e.g. COM1, /dev/ttyACM0). \
            Defaults to /dev/ttyACM0 on Linux and COM1 on Windows.",
        type=str,
        metavar="PORT",
        default="COM1" if platform.system() == "Windows" else "/dev/ttyACM0",
    )
    args = parser.parse_args()

    device = args.port
    baudrate = args.baudrate

    init_logging(getattr(logging, args.logging_level))

    logger.info("Streams API example application.")

    handler = GatewayMessageHandler(
        on_scanner_connected=on_connected,
        on_scanner_disconnected=on_disconnected,
        on_scan=on_scan,
        on_error=on_error,
        on_gateway_state_event=on_gateway_state_event,
        on_button_pressed=on_button_pressed_event,
    )

    try:
        gateway = Gateway(handler, device, baudrate)
        gateway.start()
    except ProgloveStreamsException as e:
        logging.error("Streams API exception: %s", e)
        return

    logger.info("application started, press Ctrl-C to exit")

    try:
        while True:
            time.sleep(1000)
    except KeyboardInterrupt:
        gateway.stop()
