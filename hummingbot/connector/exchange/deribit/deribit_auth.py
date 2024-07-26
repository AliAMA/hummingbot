import base64
import json
import string
from random import choices
from typing import Any, Dict

from hummingbot.connector.time_synchronizer import TimeSynchronizer
from hummingbot.core.web_assistant.auth import AuthBase
from hummingbot.core.web_assistant.connections.data_types import RESTMethod, RESTRequest, WSJSONRequest, WSRequest


class DeribitAuth(AuthBase):
    def __init__(self, client_id: str, client_secret: str, time_provider: TimeSynchronizer):
        self.client_id = client_id
        self.client_secret = client_secret
        self.time_provider = time_provider

    async def rest_authenticate(self, request: RESTRequest) -> RESTRequest:
        """
        Adds the server time and the signature to the request, required for authenticated interactions. It also adds
        the required parameter in the request header.
        :param request: the request to be configured for authenticated interaction
        """
        if request.method == RESTMethod.POST:
            request.data = self.add_auth_to_params(params=json.loads(request.data))
        else:
            request.params = self.add_auth_to_params(params=request.params)

        headers = {}
        if request.headers is not None:
            headers.update(request.headers)
        headers.update(self.authentication_headers())
        request.headers = headers

        return request

    async def ws_authenticate(self, request: WSJSONRequest) -> WSRequest:
        """
        This method is intended to configure a websocket request to be authenticated.
        """
        payload = {
            "jsonrpc": "2.0",
            "method": "public/auth",
            "id": 0,
            "params": {
                "grant_type": "client_credentials",
                "scope": "session:humbot-" + ''.join(choices(string.ascii_lowercase + string.digits, k=8)) + " expires:2592000",
                "client_id": self.client_id,
                "client_secret": self.client_secret
            }
        }

        request.payload = payload
        self.logger().debug(f"ws_authenticate payload: {payload}")

        return request

    def authentication_headers(self) -> Dict[str, Any]:
        param = f"{self.client_id}:{self.client_secret}"
        headers = {
            "Authorization": f"Basic {base64.b64encode(param.encode())}"
        }

        return headers
