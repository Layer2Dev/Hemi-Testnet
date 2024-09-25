import random
import logging

from typing import Awaitable

from asyncio import (
    create_task,
    gather,
    sleep,
    run,
)

from loguru import logger
from config import *

from src.utils.data.mappings import module_handlers
from src.utils.proxy_manager import Proxy

from src.utils.data.helper import (
    private_keys,
    active_module,
    proxies,
)

logging.getLogger("asyncio").setLevel(logging.CRITICAL)


async def process_pattern(private_key: str, pattern: str, proxy: Proxy | None) -> None:
    await module_handlers[pattern](private_key, proxy)


async def process_key(private_key: str, proxy: str) -> None:
    patterns = active_module.copy()
    random.shuffle(patterns)

    if proxy:
        change_link = None
        if MOBILE_PROXY:
            proxy_url, change_link = proxy.split('|')
        else:
            proxy_url = proxy

        proxy = Proxy(proxy_url=f'http://{proxy_url}', change_link=change_link)

        if ROTATE_IP and MOBILE_PROXY:
            await proxy.change_ip()

    pattern_tasks = []
    if 'hemiswap' in patterns:
        patterns.remove('hemiswap')
        patterns.insert(0, 'hemiswap')
    if 'bridge_to_hemi' in patterns:
        patterns.remove('bridge_to_hemi')
        patterns.insert(0, 'bridge_to_hemi')
    if 'bridge_to_sepolia' in patterns:
        patterns.remove('bridge_to_sepolia')
        patterns.insert(0, 'bridge_to_sepolia')

    for pattern in patterns:
        task = create_task(process_pattern(private_key, pattern, proxy))
        await task
        pattern_tasks.append(task)
        time_to_pause = random.randint(PAUSE_BETWEEN_MODULES[0], PAUSE_BETWEEN_MODULES[1]) \
            if isinstance(PAUSE_BETWEEN_MODULES, list) else PAUSE_BETWEEN_MODULES

        logger.info(f'Sleeping {time_to_pause} seconds before next module...')
        await sleep(time_to_pause)

    await gather(*pattern_tasks)


async def main() -> None:
    proxy_index = 0

    tasks = []
    random.shuffle(private_keys)
    for private_key in private_keys:
        proxy = proxies[proxy_index]
        proxy_index = (proxy_index + 1) % len(proxies)
        task = create_task(process_key(private_key, proxy))

        time_to_pause = random.randint(PAUSE_BETWEEN_WALLETS[0], PAUSE_BETWEEN_WALLETS[1]) \
            if isinstance(PAUSE_BETWEEN_WALLETS, list) else PAUSE_BETWEEN_WALLETS
        logger.info(f'Sleeping {time_to_pause} seconds before next wallet...')
        await sleep(time_to_pause)

        tasks.append(task)

    if tasks:
        await gather(*tasks)


def start_event_loop(awaitable: Awaitable[None]) -> None:
    run(awaitable)


if __name__ == '__main__':
    start_event_loop(main())
