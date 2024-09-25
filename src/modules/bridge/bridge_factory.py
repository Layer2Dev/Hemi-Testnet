from typing import Callable, Optional
from eth_typing import ChecksumAddress
from web3.contract import AsyncContract
from web3.types import TxParams

from src.modules.bridge.hemi_bridge.hemi_bridge_tx import create_hemi_bridge_tx
from src.modules.bridge.sepolia_bridge.sepolia_bridge_tx import create_sepolia_bridge_tx

from src.utils.abc.abc_bridge import ABCBridge
from src.models.bridge import BridgeConfig
from src.models.contracts import *
from src.utils.proxy_manager import Proxy
from loguru import logger

from src.models.token import Token


def create_bridge_class(
        class_name: str,
        contract_data,
        name: str,
        bridge_tx_function: Callable
) -> type:
    class BridgeClass(ABCBridge):
        def __init__(
                self,
                private_key: str,
                bridge_config: BridgeConfig,
                proxy: Proxy | None
        ):
            contract_address = contract_data.address
            abi = contract_data.abi

            super().__init__(
                private_key=private_key,
                proxy=proxy,
                bridge_config=bridge_config,
                contract_address=contract_address,
                abi=abi,
                name=name
            )

        def __str__(self) -> str:
            return f'{self.__class__.__name__} | [{self.wallet_address}]'

        async def create_bridge_transaction(
                self, contract: Optional[AsyncContract], bridge_config: BridgeConfig, amount: int
        ) -> TxParams:
            return await bridge_tx_function(self, contract, bridge_config, amount)

    BridgeClass.__name__ = class_name
    return BridgeClass


HemiBridge = create_bridge_class(
    class_name='HemiBridge',
    contract_data=HemiBridgeData,
    name='Hemi Bridge',
    bridge_tx_function=create_hemi_bridge_tx
)

SepoliaBridge = create_bridge_class(
    class_name='SepoliaBridge',
    contract_data=TestnetBridgeData,
    name='Sepolia Bridge',
    bridge_tx_function=create_sepolia_bridge_tx
)
