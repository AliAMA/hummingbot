from hummingbot.core.api_throttler.data_types import RateLimit
from hummingbot.core.data_type.in_flight_order import OrderState

MAX_ORDER_ID_LEN = 32

# Base URL
REST_URL = "https://www.deribit.com/api"
WSS_URL = "wss://www.deribit.com/ws/api"
DEFAULT_DOMAIN = "main"

BASE_PATH_URL = {
    "main": REST_URL,
    "test": "https://test.deribit.com/api",
}

WS_VERSION = "v2"
PUBLIC_API_VERSION = "v2"
PRIVATE_API_VERSION = "v2"


SERVER_TIME_PATH_URL = "/public/get_time"
INSTRUMENTS_PATH_URL = "/public/get_instruments"


WS_HEARTBEAT_TIME_INTERVAL = 30

# Binance params

SIDE_BUY = "BUY"
SIDE_SELL = "SELL"

TIME_IN_FORCE_GTD = "good_til_day"  # Good till day
TIME_IN_FORCE_GTC = "good_til_cancelled"  # Good till cancelled
TIME_IN_FORCE_IOC = "immediate_or_cancel"  # Immediate or cancel
TIME_IN_FORCE_FOK = "fill_or_kill"  # Fill or kill

# Rate Limit Type
NON_MATCHING_ENGINE = "NON_MATCHING_ENGINE"
MATCHING_ENGINE_TRADING = "MATCHING_ENGINE_TRADING"
MATCHING_ENGINE_SPOT = "MATCHING_ENGINE_SPOT"
MATCHING_ENGINE_MAX_QUOTES = "MATCHING_ENGINE_MAX_QUOTES"
MATCHING_ENGINE_MAX_MASS_QUOTES = "MATCHING_ENGINE_MAX_MASS_QUOTES"
MATCHING_ENGINE_GUARANTEED_MASS_QUOTES = "MATCHING_ENGINE_GUARANTEED_MASS_QUOTES"
MATCHING_ENGINE_CANCEL_ALL = "MATCHING_ENGINE_CANCEL_ALL"

# Rate Limit time intervals
ONE_MINUTE = 60
ONE_SECOND = 1
ONE_DAY = 86400

# Order States
ORDER_STATE = {
    "untriggered": OrderState.PENDING_CREATE,
    "open": OrderState.OPEN,
    "filled": OrderState.FILLED,
    "cancelled": OrderState.CANCELED,
    "rejected": OrderState.FAILED,
}

# Websocket event types
DIFF_EVENT_TYPE = "depthUpdate"
TRADE_EVENT_TYPE = "trade"

RATE_LIMITS = [
    # Pools
    RateLimit(limit_id=NON_MATCHING_ENGINE, limit=20, time_interval=ONE_SECOND),
    RateLimit(limit_id=MATCHING_ENGINE_TRADING, limit=50, time_interval=10 * ONE_SECOND),
    RateLimit(limit_id=MATCHING_ENGINE_SPOT, limit=50, time_interval=10 * ONE_SECOND),
    RateLimit(limit_id=MATCHING_ENGINE_MAX_QUOTES, limit=5000, time_interval=10 * ONE_SECOND),
    RateLimit(limit_id=MATCHING_ENGINE_MAX_MASS_QUOTES, limit=10, time_interval=ONE_SECOND),
    RateLimit(limit_id=MATCHING_ENGINE_GUARANTEED_MASS_QUOTES, limit=2, time_interval=ONE_SECOND),
    RateLimit(limit_id=MATCHING_ENGINE_CANCEL_ALL, limit=5, time_interval=ONE_SECOND),
    RateLimit(limit_id=SERVER_TIME_PATH_URL, limit=2, time_interval=ONE_SECOND),
]

ORDER_NOT_EXIST_ERROR_CODE = 10004
ORDER_NOT_EXIST_MESSAGE = "order_not_found"
