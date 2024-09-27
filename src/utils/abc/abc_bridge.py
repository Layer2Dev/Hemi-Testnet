from abc import ABC, abstractmethod
from asyncio import sleep
from distutils.command.config import config
from typing import Optional

from web3.contract import AsyncContract
from web3.types import TxParams
from loguru import logger

from config import RETRIES, PAUSE_BETWEEN_RETRIES
from src.models.bridge import BridgeConfig
from src.utils.data.chains import chain_mapping
from src.utils.request_client.request_client import RequestClient
from src.utils.user.account import Account
from src.utils.proxy_manager import Proxy
from src.utils.wrappers.decorators import retry


class ABCBridge(ABC, Account, RequestClient):
    def __init__(
            self,
            private_key: str,
            proxy: Proxy | None,
            bridge_config: BridgeConfig,
            contract_address: str,
            abi: str,
            name: str
    ):
        self.config = bridge_config
        self.name = name

        rpc = self.config.from_chain.rpc

        Account.__init__(self, private_key=private_key, rpc=rpc, proxy=proxy)
        RequestClient.__init__(self, proxy=proxy)

        self.contract_address = contract_address
        self.abi = abi
        self.scan = chain_mapping[self.config.from_chain.chain_name.upper()].scan

    @abstractmethod
    async def create_bridge_transaction(
            self, contract: Optional[AsyncContract], bridge_config: BridgeConfig, amount: int
    ) -> TxParams:
        """Creates transaction for bridge"""

    @retry(
        retries=RETRIES,
        delay=PAUSE_BETWEEN_RETRIES,
        backoff=1.5
    )
    async def bridge(self) -> None:
        native_balance = await self.get_wallet_balance(is_native=True)

        if native_balance == 0:
            logger.error(f'Your native balance is 0 | [{self.wallet_address}]')
            return
        to_chain_account = Account(private_key=self.private_key, rpc=self.config.to_chain.rpc, proxy=self.proxy)

        balance_before_bridge = await to_chain_account.get_wallet_balance(
            is_native=True if self.config.to_chain.native_token == self.config.to_token.name else False,
            address=self.config.to_token.address
        )

        bridge_token_balance = await self.get_wallet_balance(
            is_native=True if self.config.from_chain.native_token == self.config.from_token.name else False,
            address=self.config.from_token.address
        )

        if bridge_token_balance == 0:
            logger.error(f'{self.config.from_token.name} balance is 0 | [{self.wallet_address}]')
            return

        contract = None
        if self.contract_address and self.abi:
            contract = self.load_contract(
                address=self.contract_address,
                web3=self.web3,
                abi=self.abi
            )

        amount = await self.create_amount(
            is_native=True if self.config.from_chain.native_token == self.config.from_token.name else False,
            from_token_address=self.config.from_token.address,
            web3=self.web3,
            amount=self.config.amount
        )
        if self.config.use_percentage:
            amount = int(bridge_token_balance * self.config.bridge_percentage)

        if self.contract_address and self.config.from_chain.native_token != self.config.from_token.name:
            await self.approve_token(
                amount=amount,
                private_key=self.private_key,
                from_token_address=self.config.from_token.address,
                spender=self.contract_address,
                address_wallet=self.wallet_address,
                web3=self.web3
            )

        tx, to_address = await self.create_bridge_transaction(contract, self.config, amount)
        if to_address and self.config.from_chain.native_token != self.config.from_token.name:
            await self.approve_token(
                amount=amount,
                private_key=self.private_key,
                from_token_address=self.config.from_token.address,
                spender=to_address,
                address_wallet=self.wallet_address,
                web3=self.web3
            )

        gas_limit = await self.web3.eth.estimate_gas(tx)
        tx.update({'gas': gas_limit})

        tx_hash = None
        confirmed = None
        try:
            tx_hash = await self.sign_transaction(tx)
            confirmed = await self.wait_until_tx_finished(tx_hash)
        except Exception as ex:
            logger.error(f'Something went wrong {ex}')

        if confirmed:
            logger.success(
                f'Successfully bridged on {self.name} {self.config.from_token.name} '
                f'({self.config.from_chain.chain_name}) => {self.config.to_token.name} '
                f'({self.config.to_chain.chain_name}) | TX: {self.scan}/{tx_hash}'
            )
            await self.wait_for_bridge(account=to_chain_account, balance_before_bridge=balance_before_bridge)

    async def wait_for_bridge(self, account: Account, balance_before_bridge: int) -> None:
        logger.info(f'Waiting for {self.config.to_token.name} to arrive in {self.config.to_chain.chain_name}...')
        while True:
            try:
                balance = await account.get_wallet_balance(
                    is_native=True if self.config.to_chain.native_token == self.config.to_token.name else False,
                    address=self.config.to_token.address
                )
                if balance > balance_before_bridge:
                    logger.success(f'{self.config.to_token.name} has arrived | [{self.wallet_address}]')
                    break
                await sleep(20)
            except Exception as ex:
                logger.error(f'Something went wrong {ex}')
                await sleep(10)
                continue
