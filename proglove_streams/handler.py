"""Streams API handler protocol."""
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from streams_api.customer_integrations.button_pressed.model import ButtonPressedStream
from streams_api.customer_integrations.errors.model import ErrorsStream
from streams_api.customer_integrations.gateway_state_event.model import (
    GatewayStateEventStream,
)
from streams_api.customer_integrations.scan.model import ScanStream
from streams_api.customer_integrations.scanner_state.model import ScannerStateStream

from proglove_streams.client import Client


@dataclass
class Handler:
    """Streams API message handler.

    This handler is dispatching the different parsed Streams API messages
    through callbacks.

    """

    on_scan: Optional[Callable[[Client, ScanStream], None]] = None
    on_scanner_connected: Optional[Callable[[Client, ScannerStateStream], None]] = None
    on_scanner_disconnected: Optional[
        Callable[[Client, ScannerStateStream], None]
    ] = None
    on_error: Optional[Callable[[Client, ErrorsStream], None]] = None
    on_gateway_state_event: Optional[
        Callable[[Client, GatewayStateEventStream], None]
    ] = None
    on_button_pressed: Optional[Callable[[Client, ButtonPressedStream], None]] = None

    def handle(self, _client: Client, _event: Dict[str, Any]) -> None:
        """Handle the events."""
