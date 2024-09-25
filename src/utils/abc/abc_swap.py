from typing import Optional, List
from abc import ABC, abstractmethod
from asyncio import sleep

from eth_typing import ChecksumAddress
from web3.contract import AsyncContract
from web3.types import TxParams
from loguru import logger

from src.utils.proxy_manager import Proxy
from src.utils.user.account import Account
from config import RETRIES, PAUSE_BETWEEN_RETRIES
from src.utils.wrappers.decorators import retry
from src.models.swap import SwapConfig, Token
from src.utils.request_client.request_client import RequestClient


class ABCSwap(ABC, Account, RequestClient):
    def __init__(
            self,
            private_key: str,
            config: SwapConfig,
            proxy: Proxy | None,
            contract_address: Optional[str],
            abi: Optional[str],
            name: str
    ):

        Account.__init__(self, private_key, proxy=proxy)
        RequestClient.__init__(self, proxy=proxy)

        self.private_key = private_key
        self.config = config
        self.contract_address = contract_address
        self.abi = abi
        self.name = name

    @abstractmethod
    async def get_amount_out(self, contract: AsyncContract, amount: int, from_token_address: ChecksumAddress,
                             to_token_address: ChecksumAddress) -> int:
        """Gets output amount"""

    @abstractmethod
    async def create_swap_tx(self, from_token: str, to_token: str, contract: AsyncContract, amount_out: int,
                             from_token_address: ChecksumAddress, to_token_address: ChecksumAddress,
                             amount: int) -> tuple[List[TxParams], Optional[str]]:
        """Creates swap transaction"""

    @retry(
        retries=RETRIES,
        delay=PAUSE_BETWEEN_RETRIES,
        backoff=1.5
    )
    async def swap(self) -> Optional[bool | str]:
        contract = self.load_contract(
            self.contract_address, self.web3, self.abi
        )

        is_native = self.config.from_token.name.upper() == 'ETH'
        amount = await self.create_amount(
            is_native=is_native,
            from_token_address=self.config.from_token.address,
            web3=self.web3,
            amount=self.config.amount
        )
        balance = await self.get_wallet_balance(
            is_native=is_native,
            address=self.config.from_token.address
        )
        if balance == 0:
            logger.error(f'Your balance is 0 | {self.wallet_address}')
            return 'ZeroBalance'
        if self.config.swap_all_balance is True and self.config.from_token.name.upper() == 'ETH':
            logger.error(
                "You can't use swap_all_balance = True with ETH token."
                "Using amount_from, amount_to")
        if self.config.swap_all_balance is True and self.config.from_token.name.upper() != 'ETH':
            logger.debug(f"Token name: {self.config.from_token.name}")
            amount = balance

        if self.config.use_percentage is True:
            amount = int(balance * self.config.swap_percentage)

        if amount > balance:
            logger.error(f'Not enough balance for wallet {self.wallet_address}')
            return

        amount_out = await self.get_amount_out(
            contract,
            amount,
            self.web3.to_checksum_address(self.config.from_token.address),
            self.web3.to_checksum_address(self.config.to_token.address)
        )

        if self.config.from_token.name.upper() != 'ETH' and self.contract_address is not None:
            await self.approve_token(
                amount,
                self.private_key,
                self.config.from_token.address,
                self.contract_address,
                self.wallet_address, self.web3
            )

        transactions = None
        while True:
            try:
                transactions, to_address = await self.create_swap_tx(
                    self.config.from_token.name,
                    self.config.to_token.name,
                    contract,
                    amount_out,
                    self.web3.to_checksum_address(self.config.from_token.address),
                    self.web3.to_checksum_address(self.config.to_token.address),
                    amount
                )

                if to_address and self.config.from_token.name.upper() != 'ETH':
                    await self.approve_token(
                        amount,
                        self.private_key,
                        self.config.from_token.address,
                        to_address,
                        self.wallet_address,
                        self.web3
                    )
                break
            except ValueError as ex:
                if 'max fee per gas less than block base fee' in str(ex):
                    logger.error(ex)
                    await sleep(1)
                    continue
            except Exception as ex:
                logger.error(f'Something went wrong | {ex}')
                break

        if transactions is None:
            return

        tx_hash = None
        confirmed = None

        for tx in transactions:
            while True:
                try:
                    gas = await self.web3.eth.estimate_gas(tx)
                    tx.update({'gas': int(gas * 1.05)})
                    tx_hash = await self.sign_transaction(tx)
                    confirmed = await self.wait_until_tx_finished(tx_hash)
                    await sleep(2)
                except Exception as ex:
                    if 'nonce' in str(ex):
                        tx.update({'nonce': await self.web3.eth.get_transaction_count(self.wallet_address)})
                        continue
                    logger.error(f'Something went wrong {ex}')
                    return False
                break

        if confirmed:
            logger.success(
                f'Successfully swapped {"all" if self.config.swap_all_balance is True and self.config.from_token.name.lower() != "eth" and self.config.use_percentage is False else f"{int(self.config.swap_percentage * 100)}%" if self.config.use_percentage is True else self.config.amount} {self.config.from_token.name} tokens => {self.config.to_token.name} | TX: https://testnet.explorer.hemi.xyz/tx/{tx_hash}')
            return True
