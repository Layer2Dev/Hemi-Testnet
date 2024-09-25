import json

from time import time
from typing import List, Optional, Callable
from asyncio import sleep

import pyuseragents
from eth_abi import encode
from eth_typing import ChecksumAddress
from web3 import AsyncWeb3
from web3.contract import Contract
from web3.types import TxParams


async def create_hemiswap_swap_tx(
        self, from_token: str, to_token: str, contract: Contract, amount_out: int,
        from_token_address: ChecksumAddress, to_token_address: ChecksumAddress,
        amount: int
) -> tuple[List[TxParams], Optional[str]]:
    amount_out = await get_amount_out(
        to_token,
        amount,
        self.make_request,
        self.wallet_address
    )

    bytes_amount = encode(
        ['uint256', 'uint256'],
        [2, amount]

    )
    path = encode(
        ['address', 'uint24', 'address'],
        [to_token_address, 3000, from_token_address]
    )
    corrected_path = '0x' + path.hex()[24:]
    corrected_path = corrected_path.replace(
        "0000000000000000000000000000000000000000000000000000000000000bb80000000000000000000000000",
        "000bb80"
    )

    bytes_path = encode(
        ['uint256', 'uint256', 'uint256', 'bytes', 'uint256'],
        [1, int(amount_out * 0.95), amount, self.web3.to_bytes(hexstr=corrected_path), 0]
    )
    bytes_empty = encode(
        ['uint256', 'uint256'],
        [1, 0]
    )
    data = [bytes_amount, bytes_path, bytes_empty]

    if from_token == 'ETH' and to_token in ['DAI', 'USDT', 'USDC']:
        prefix = '0x0b010c'
    else:
        prefix = '0x0a000c'
    tx = await contract.functions.execute(
        self.web3.to_bytes(hexstr=prefix),
        data,
        int(time() + 600)
    ).build_transaction({
        'from': self.wallet_address,
        'value': amount if from_token.upper() == 'ETH' else 0,
        'nonce': await self.web3.eth.get_transaction_count(self.wallet_address),
        'gasPrice': int(await self.web3.eth.gas_price),
    })

    return [tx], None


async def get_amount_out(to_token_address: str, amount: int, request_function: Callable,
                         wallet_address: ChecksumAddress) -> int:
    headers = {
        'sec-ch-ua-platform': '"Windows"',
        'Referer': 'https://swap.hemi.xyz/',
        'User-Agent': pyuseragents.random(),
        'Content-Type': 'text/plain;charset=UTF-8',
    }

    data = {
        "tokenInChainId": 743111,
        "tokenIn": "ETH",
        "tokenOutChainId": 743111,
        "tokenOut": to_token_address,
        "amount": str(amount),
        "sendPortionEnabled": True,
        "type": "EXACT_INPUT",
        "intent": "quote",
        "configs": [
            {
                "protocols": ["V2", "V3", "MIXED"],
                "enableUniversalRouter": True,
                "routingType": "CLASSIC",
                "recipient": wallet_address,
                "enableFeeOnTransferFeeFetching": True
            }
        ]
    }

    while True:
        try:
            response_json = await request_function(
                method='POST',
                url='https://hgc8sm30t0.execute-api.eu-central-1.amazonaws.com/production/v2/quote',
                headers=headers,
                data=json.dumps(data)
            )
            amount_out = int(response_json['quote']['quote'])
            return amount_out
        except (TypeError, IndexError):
            await sleep(1)
