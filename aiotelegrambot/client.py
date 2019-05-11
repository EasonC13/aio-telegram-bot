import aiohttp
import logging
from json import loads
from typing import Dict, Optional, Union

logger = logging.getLogger(__name__)


class Client:
    base_url = "https://api.telegram.org/bot"

    def __init__(self, token: str, **kwargs):
        self._url = "{}{}/".format(self.base_url, token)

        session_kwargs = {
            "timeout": aiohttp.ClientTimeout(total=1)
        }
        session_kwargs.update(kwargs)

        self._session = aiohttp.ClientSession(**session_kwargs)

    async def close(self):
        await self._session.close()

    async def get_updates(
            self,
            offset: Optional[int] = None,
            limit: Optional[int] = None,
            timeout: Optional[int] = None
    ) -> Optional[Dict]:
        params = {}
        if offset:
            params["offset"] = offset
        if limit:
            params["limit"] = limit
        if timeout:
            params["timeout"] = timeout
        return await self.request("get", "getUpdates", params=params)

    async def send_message(self, text: str, chat_id: Union[int, str]):
        await self.request("get", "sendMessage", params={"chat_id": chat_id, "text": text})

    async def request(self, method: str, api: str, **kwargs) -> Optional[Dict]:
        url = self._url + api

        async with getattr(self._session, method)(url, **kwargs) as response:
            data = loads(await response.text())
            if response.status == 200:
                if data["ok"]:
                    return data
                else:
                    logger.error("Unsuccessful request", extra=data)
            else:
                logger.error("Status: {}".format(response.status), extra=data)
                if response.status >= 500:
                    raise aiohttp.ClientResponseError(
                        response.request_info,
                        response.history,
                        status=response.status,
                        message=response.reason,
                        headers=response.headers
                    )