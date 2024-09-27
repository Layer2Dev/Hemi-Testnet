from eth_abi import encode
from loguru import logger

from config import PAUSE_BETWEEN_RETRIES, RETRIES
from src.models.contracts import GnosisSafeData
from src.utils.request_client.request_client import RequestClient
from src.utils.user.account import Account
from src.utils.proxy_manager import Proxy
from src.utils.wrappers.decorators import retry


class GnosisSafe(Account, RequestClient):
    def __init__(
            self,
            private_key: str,
            proxy: Proxy | None
    ):
        Account.__init__(self, private_key=private_key, proxy=proxy)
        RequestClient.__init__(self, proxy=proxy)

    def __str__(self) -> str:
        return f'[{self.wallet_address}] | [{self.__class__.__name__}]'

    @retry(
        delay=PAUSE_BETWEEN_RETRIES,
        retries=RETRIES,
        backoff=1.5
    )
    async def create_safe(self) -> None:
        contract = self.load_contract(
            address=GnosisSafeData.address,
            web3=self.web3,
            abi=GnosisSafeData.abi
        )

        data = '0xb63e800d' + encode(
            ['address[]', 'uint256', 'address', 'bytes', 'address', 'address', 'uint256', 'address'],
            [
                [self.wallet_address],
                1,
                self.web3.to_checksum_address('0x0000000000000000000000000000000000000000'),
                b'',
                self.web3.to_checksum_address('0xf48f2B2d2a534e402487b3ee7C18c33Aec0Fe5e4'),
                self.web3.to_checksum_address('0x0000000000000000000000000000000000000000'),
                0,
                self.web3.to_checksum_address('0x0000000000000000000000000000000000000000')
            ]
        ).hex()

        tx = await contract.functions.createProxyWithNonce(
            self.web3.to_checksum_address('0x3E5c63644E683549055b9Be8653de26E0B4CD36E'),
            self.web3.to_bytes(hexstr=data),
            0
        ).build_transaction({
            'from': self.wallet_address,
            'value': 0,
            'nonce': await self.web3.eth.get_transaction_count(self.wallet_address),
            'gasPrice': await self.web3.eth.gas_price,
        })
        tx_hash = await self.sign_transaction(tx)
        confirmed = await self.wait_until_tx_finished(tx_hash)

        if confirmed:
            logger.success(
                f'Successfully created safe | Address: [{self.wallet_address}] |'
                f' TX: https://testnet.explorer.hemi.xyz/tx/{tx_hash}'
            )

    async def check_safe(self) -> None:
        ...
