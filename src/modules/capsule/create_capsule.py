import random

import pyuseragents
from aiohttp import ClientSession
from asyncio import sleep

from eth_abi import encode
from loguru import logger
from src.utils.proxy_manager import Proxy
from src.utils.request_client.request_client import RequestClient
from src.utils.user.account import Account
from src.utils.data.chains import chain_mapping
from src.models.contracts import CapsuleData
from src.utils.data.tokens import tokens


class Capsule(Account, RequestClient):
    def __init__(
            self,
            private_key: str,
            proxy: Proxy | None,
    ):
        Account.__init__(self, private_key, proxy=proxy)
        RequestClient.__init__(self, proxy=proxy)

    def __str__(self) -> str:
        return f'[{self.__class__.__name__}] | [{self.wallet_address}] | Creating capsule...'

    async def create_capsule(self) -> None:
        url = await self.create_metadata()
        contract = self.load_contract(
            address=CapsuleData.address,
            web3=self.web3,
            abi=CapsuleData.abi
        )

        token_list = ['DAI', 'USDT', 'USDC']
        random.shuffle(token_list)
        while True:
            if not token_list:
                logger.error('You have no tokens')
                return
            token, token_address = self.choose_token(token_list)
            token_balance = await self.get_wallet_balance(is_native=False, address=token_address)
            if token_balance != 0:
                break
            token_list.remove(token)

        amount = int(token_balance * random.uniform(0.1, 0.3))
        await self.approve_token(
            amount=amount,
            private_key=self.private_key,
            from_token_address=token_address,
            spender='0x9398aa1fbb6a06f5790822e60db8aaceb51a2bca',
            address_wallet=self.wallet_address,
            web3=self.web3
        )
        token_data_bytes = encode(
            ['uint256', 'address', 'uint256', 'uint256'],
            [1, self.web3.to_checksum_address(token_address), 0, amount]
        )
        tx = await contract.functions.shipPackage(
            [
                [
                    token_data_bytes
                ],
                url
            ],
            [
                self.web3.to_bytes(hexstr="0x0000000000000000000000000000000000000000000000000000000000000000"),
                0,
                self.web3.to_bytes(hexstr="0x0000000000000000000000000000000000000000"),
                0
            ],
            self.wallet_address
        ).build_transaction({
            'from': self.wallet_address,
            'value': int(0.001 * 10 ** 18),
            'nonce': await self.web3.eth.get_transaction_count(self.wallet_address),
            'gasPrice': await self.web3.eth.gas_price,
        })

        tx_hash = await self.sign_transaction(tx)
        confirmed = await self.wait_until_tx_finished(tx_hash)

        if confirmed:
            logger.success(
                f'Successfully created a capsule | Address: [{self.wallet_address}] |'
                f' TX: https://testnet.explorer.hemi.xyz/tx/{tx_hash}'
            )

    async def create_metadata(self) -> str:
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'ru,en-US;q=0.9,en;q=0.8',
            'content-type': 'application/json',
            'origin': 'https://app.capsulelabs.xyz',
            'priority': 'u=1, i',
            'referer': 'https://app.capsulelabs.xyz/',
            'user-agent': pyuseragents.random(),
        }

        json_data = {
            'name': 'Hemi Tunneled DAI Transaction',
        }

        response_json = await self.make_request(
            method='POST',
            url='https://app.capsulelabs.xyz/api/create-metadata',
            headers=headers,
            json=json_data
        )
        url = response_json['tokenURI']
        return url

    @staticmethod
    def choose_token(token_list: list[str]) -> tuple[str, str]:
        token = random.choice(token_list)
        token_address = tokens['HEMI'][token]

        return token, token_address
