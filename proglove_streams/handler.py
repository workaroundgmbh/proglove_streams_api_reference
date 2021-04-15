"""Streams API handler protocol."""
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass

from proglove_streams.client import Client

from proglove_streams.models.error import (
    ErrorEvent
)
from proglove_streams.models.gateway_state import (
    GatewayStateEvent,
)
from proglove_streams.models.scan import (
    ScanEvent
)
from proglove_streams.models.scanner_state import (
    ScannerStateEvent
)
from proglove_streams.models.button_pressed import (
    ButtonPressedEvent
)


@dataclass
class Handler:
    """Streams API message handler.

    This handler is dispatching the different parsed Streams API messages
    through callbacks.

    """
    on_scan: Optional[
        Callable[[Client, ScanEvent], None]
    ] = None
    on_scanner_connected: Optional[
        Callable[[Client, ScannerStateEvent], None]
    ] = None
    on_scanner_disconnected: Optional[
        Callable[[Client, ScannerStateEvent], None]
    ] = None
    on_error: Optional[
        Callable[[Client, ErrorEvent], None]
    ] = None
    on_gateway_state_event: Optional[
        Callable[[Client, GatewayStateEvent], None]
    ] = None
    on_button_pressed: Optional[
        Callable[[Client, ButtonPressedEvent], None]
    ] = None

    def handle(self, _client: Client, _event: Dict[str, Any]):
        """Handle the events."""
