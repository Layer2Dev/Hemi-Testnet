from typing import Optional, Callable, Tuple
from asyncio import sleep

from web3 import AsyncWeb3
from web3.contract import AsyncContract
from web3.types import TxParams

from src.models.bridge import BridgeConfig


async def create_sepolia_bridge_tx(self, contract: Optional[AsyncContract], bridge_config: BridgeConfig,
                                   amount: int) -> Tuple[TxParams, None]:

    amount_out = await get_amount_out(amount, self.make_request, self.web3)
    tx = await contract.functions.swapAndBridge(
        amount,
        amount_out,
        161,
        self.wallet_address,
        self.wallet_address,
        self.web3.to_checksum_address('0x0000000000000000000000000000000000000000'),
        b''
    ).build_transaction({
        'from': self.wallet_address,
        'value': amount + 25254000000000,
        'nonce': await self.web3.eth.get_transaction_count(self.wallet_address),
        "gasPrice": await self.web3.eth.gas_price,
    })

    return tx, None


async def get_amount_out(amount_in: int, request_function: Callable, web3: AsyncWeb3) -> int:
    amount_in_hex = web3.to_hex(amount_in)[2:]
    if len(amount_in_hex) < 13:
        amount_in_hex = f"{'0' * (13 - len(amount_in_hex))}{amount_in_hex}"
    elif len(amount_in_hex) > 13:
        amount_in_hex = amount_in_hex[:13]

    json_data = [
        {
            "method": "eth_call",
            "params": [
                {
                    "to": "0xb27308f9f90d607463bb33ea1bebb41c27ce5ab6",
                    "data": f"0xf7729d4300000000000000000000000082af49447d8a07e3bd95bd0d56f35241523fbab1000000000000000000000000e71bdfe1df69284f00ee185cf0d95d0c7680c0d40000000000000000000000000000000000000000000000000000000000000bb8000000000000000000000000000000000000000000000000000{amount_in_hex}0000000000000000000000000000000000000000000000000000000000000000",
                },
                "latest",
            ],
            "id": 82,
            "jsonrpc": "2.0",
        },
    ]
    while True:
        try:
            response_json = await request_function(
                method='POST',
                url='https://arb1.arbitrum.io/rpc',
                json=json_data
            )
            amount_out_hex = int(response_json[0]["result"], 16)

            amount_out = float(amount_out_hex) * 0.95
            amount_out = web3.to_wei(amount_out, "ether")
            if len(str(amount_out)) > 18:
                amount_out = int(amount_out / 1e18)

            return amount_out
        except (TypeError, IndexError) as ex:
            await sleep(1)
