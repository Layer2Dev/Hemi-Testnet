from typing import Optional, Tuple, Any

from web3.contract import AsyncContract
from web3.types import TxParams

from src.models.bridge import BridgeConfig


async def create_hemi_bridge_tx(self, contract: Optional[AsyncContract], bridge_config: BridgeConfig,
                                amount: int) -> Tuple[TxParams, None]:
    # l2_gas = int(await self.web3.eth.gas_price)
    data = b''
    tx = await contract.functions.depositETH(
        200_000,
        data
    ).build_transaction({
        'from': self.wallet_address,
        'value': amount,
        'nonce': await self.web3.eth.get_transaction_count(self.wallet_address),
        "gasPrice": int(await self.web3.eth.gas_price * 1.05),
    })

    return tx, None
