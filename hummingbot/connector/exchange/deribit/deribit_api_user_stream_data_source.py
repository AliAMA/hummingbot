import asyncio
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from hummingbot.connector.exchange.deribit import deribit_constants as CONSTANTS, deribit_web_utils as web_utils
from hummingbot.connector.exchange.deribit.deribit_auth import DeribitAuth
from hummingbot.core.data_type.user_stream_tracker_data_source import UserStreamTrackerDataSource
from hummingbot.core.web_assistant.connections.data_types import WSJSONRequest
from hummingbot.core.web_assistant.web_assistants_factory import WebAssistantsFactory
from hummingbot.core.web_assistant.ws_assistant import WSAssistant
from hummingbot.logger import HummingbotLogger

if TYPE_CHECKING:
    from hummingbot.connector.exchange.deribit.deribit_exchange import DeribitExchange


class DeribitAPIUserStreamDataSource(UserStreamTrackerDataSource):
    LISTEN_KEY_KEEP_ALIVE_INTERVAL = 1800  # Recommended to Ping/Update listen key to keep connection alive
    HEARTBEAT_TIME_INTERVAL = 30.0

    _logger: Optional[HummingbotLogger] = None

    def __init__(self,
                 auth: DeribitAuth,
                 trading_pairs: List[str],
                 connector: 'DeribitExchange',
                 api_factory: WebAssistantsFactory,
                 domain: str = CONSTANTS.DEFAULT_DOMAIN):
        super().__init__()
        self._auth: DeribitAuth = auth
        self._current_listen_key = None
        self._domain = domain
        self._api_factory = api_factory

        self._listen_key_initialized_event: asyncio.Event = asyncio.Event()
        self._ping_interval = 40

    async def _get_ws_assistant(self) -> WSAssistant:
        if self._ws_assistant is None:
            self._ws_assistant = await self._api_factory.get_ws_assistant()
        return self._ws_assistant

    async def _connected_websocket_assistant(self) -> WSAssistant:
        """
        Creates an instance of WSAssistant connected to the exchange
        """
        ws: WSAssistant = await self._get_ws_assistant()
        url = f"{CONSTANTS.WSS_URL}/{CONSTANTS.WS_VERSION}"
        await ws.connect(ws_url=url, ping_timeout=CONSTANTS.WS_HEARTBEAT_TIME_INTERVAL)
        return ws

    async def _subscribe_channels(self, websocket_assistant: WSAssistant):
        """
        Subscribes to order events and balance events.

        :param ws: the websocket assistant used to connect to the exchange
        """
        try:
            heartbeat_payload = await self._get_heartbet_payload()
            heartbeat_request = WSJSONRequest(payload=heartbeat_payload)
            await websocket_assistant.send(heartbeat_request)

            orders_change_payload = {
                "jsonrpc": "2.0",
                "method": "private/subscribe",
                "id": web_utils.next_message_id(),
                "params": {
                    "channels": ["user.changes.spot.any.raw"]
                }
            }
            subscribe_order_change_request: WSJSONRequest = WSJSONRequest(payload=orders_change_payload,
                                                                          is_auth_required=True)

            balance_payload = {
                "jsonrpc": "2.0",
                "method": "private/subscribe",
                "id": web_utils.next_message_id(),
                "params": {
                    "channels": ["user.portfolio.any"]
                }
            }
            subscribe_balance_request: WSJSONRequest = WSJSONRequest(payload=balance_payload,
                                                                     is_auth_required=True)

            await websocket_assistant.send(subscribe_order_change_request)
            await websocket_assistant.send(subscribe_balance_request)

            self._last_ws_message_sent_timestamp = self._time()
            self.logger().info("Subscribed to private order changes and balance updates channels...")
        except asyncio.CancelledError:
            raise
        except Exception:
            self.logger().exception("Unexpected error occurred subscribing to user streams...")
            raise

    async def _get_heartbet_payload(self):
        return {
            "jsonrpc": "2.0",
            "id": web_utils.next_message_id(),
            "method": "public/set_heartbeat",
            "params": {
                "interval": self._ping_interval
            }
        }

    async def _process_websocket_messages(self, websocket_assistant: WSAssistant, queue: asyncio.Queue):
        while True:
            try:
                seconds_until_next_ping = self._ping_interval - (self._time() - self._last_ws_message_sent_timestamp)
                await asyncio.wait_for(
                    super()._process_websocket_messages(
                        websocket_assistant=websocket_assistant, queue=queue),
                    timeout=seconds_until_next_ping)
            except asyncio.TimeoutError:
                payload = await self._get_heartbet_payload()
                ping_request = WSJSONRequest(payload=payload)
                self._last_ws_message_sent_timestamp = self._time()
                await websocket_assistant.send(request=ping_request)

    async def _process_event_message(self, event_message: Dict[str, Any], queue: asyncio.Queue):
        if (len(event_message) > 0
                and event_message.get("type") == "message"
                and event_message.get("subject") in [CONSTANTS.ORDER_CHANGE_EVENT_TYPE, CONSTANTS.BALANCE_EVENT_TYPE]):
            queue.put_nowait(event_message)
