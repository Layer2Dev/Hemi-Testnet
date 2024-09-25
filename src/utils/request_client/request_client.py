from asyncio import sleep
from typing import Dict, Any
from loguru import logger

from aiohttp import ClientSession, TCPConnector
from aiohttp_socks import ProxyConnector

from src.utils.proxy_manager import Proxy


class RequestClient:
    def __init__(self, proxy: Proxy | None):
        self.session = ClientSession(
            connector=ProxyConnector.from_url(proxy.proxy_url, ) if proxy else TCPConnector(
                verify_ssl=False
            )
        )

    async def make_request(
            self,
            method: str = 'GET',
            url: str = None,
            headers: Dict[str, Any] = None,
            data: str = None,
            json: Dict[str, Any] = None,
            params: Dict[str, Any] = None
    ):

        async with self.session.request(
                method=method, url=url, headers=headers, data=data, params=params, json=json
        ) as response:
            try:
                response_json = await response.json()
                if response.status == 200:
                    return response_json
                elif response.status == 414:
                    await sleep(5)
                else:
                    logger.error(f'Unknown error | STATUS CODE: {response.status}')
                    return None, None

            except Exception as ex:
                logger.error(f'Something went wrong {ex}')
