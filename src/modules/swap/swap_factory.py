from typing import Callable, Optional

from eth_typing import ChecksumAddress
from web3.contract import AsyncContract
from web3.types import TxParams

from src.modules.swap.hemiswap.hemiswap_transaction import create_hemiswap_swap_tx
from src.models.contracts import *
from src.utils.abc.abc_swap import ABCSwap
from src.utils.proxy_manager import Proxy
from src.models.swap import (
    Token,
    SwapConfig
)


def create_swap_class(
        class_name: str,
        contract_data,
        name: str,
        swap_tx_function: Callable,
        amount_out_function: Optional[Callable]
) -> type:
    class SwapClass(ABCSwap):
        def __init__(
                self,
                private_key: str,
                chain_name: str = 'HEMI',
                *,
                from_token: str | list[str],
                to_token: str | list[str],
                amount: float | list[float],
                use_percentage: bool,
                swap_percentage: float | list[float],
                swap_all_balance: bool,
                proxy: Proxy | None,
                dex_name: str = name

        ):
            contract_address = contract_data.address
            abi = contract_data.abi
            swap_config = SwapConfig(
                from_token=Token(
                    chain_name=chain_name,
                    name=from_token

                ),
                to_token=Token(
                    chain_name=chain_name,
                    name=to_token
                ),
                amount=amount,
                use_percentage=use_percentage,
                swap_percentage=swap_percentage,
                swap_all_balance=swap_all_balance,
            )
            super().__init__(
                private_key=private_key,
                config=swap_config,
                proxy=proxy,
                contract_address=contract_address,
                abi=abi,
                name=name
            )

        def __str__(self) -> str:
            return f'{self.__class__.__name__} | [{self.wallet_address}]'

        async def get_amount_out(self, contract: AsyncContract, amount: int, from_token_address: ChecksumAddress,
                                 to_token_address: ChecksumAddress) -> Optional[int]:
            if amount_out_function:
                return await amount_out_function(self, contract)

        async def create_swap_tx(
                self, from_token: str, to_token: str, contract: AsyncContract, amount_out: int,
                from_token_address: ChecksumAddress, to_token_address: ChecksumAddress,
                amount: int) -> tuple[TxParams, Optional[str]]:
            return await swap_tx_function(self, from_token, to_token, contract, amount_out,
                                          from_token_address, to_token_address,
                                          amount)

    SwapClass.__name__ = class_name
    return SwapClass


HemiSwap = create_swap_class(
    class_name='HemiSwap',
    contract_data=HemiSwapData,
    name='Hemi',
    swap_tx_function=create_hemiswap_swap_tx,
    amount_out_function=None
)
