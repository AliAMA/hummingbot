from decimal import Decimal
from typing import Any, Dict

from pydantic import Field, SecretStr

from hummingbot.client.config.config_data_types import BaseConnectorConfigMap, ClientFieldData
from hummingbot.core.data_type.trade_fee import TradeFeeSchema

CENTRALIZED = True

EXAMPLE_PAIR = "ETH_USDT"
EXAMPLE_BTC_PAIR = "BTC_USDT"

DEFAULT_FEES = TradeFeeSchema(
    maker_percent_fee_decimal=Decimal("0.0"),
    taker_percent_fee_decimal=Decimal("0.0"),
)


def is_pair_information_valid(pair_info: Dict[str, Any]) -> bool:
    """
    Verifies if a trading pair is enabled to operate with based on its market information

    :param pair_info: the market information for a trading pair

    :return: True if the trading pair is enabled, False otherwise
    """
    return pair_info.get("is_active", False)


class DeribitConfigMap(BaseConnectorConfigMap):
    connector: str = Field(default="deribit", client_data=None)
    deribit_client_id: SecretStr = Field(
        default=...,
        client_data=ClientFieldData(
            prompt=lambda cm: "Enter your Deribit API Client Id",
            is_secure=True,
            is_connect_key=True,
            prompt_on_new=True,
        )
    )
    deribit_client_secret: SecretStr = Field(
        default=...,
        client_data=ClientFieldData(
            prompt=lambda cm: "Enter your Deribit API client secret key",
            is_secure=True,
            is_connect_key=True,
            prompt_on_new=True,
        )
    )

    class Config:
        title = "deribit"


KEYS = DeribitConfigMap.construct()
