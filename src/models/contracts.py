from dataclasses import dataclass


@dataclass
class ERC20:
    abi: str = open('./assets/abi/erc20.json', 'r').read()


@dataclass
class TestnetBridgeData:
    address: str = '0xfcA99F4B5186D4bfBDbd2C542dcA2ecA4906BA45'
    abi: str = open('./assets/abi/testnet_bridge.json', 'r').read()


@dataclass
class HemiBridgeData:
    address: str = '0xc94b1BEe63A3e101FE5F71C80F912b4F4b055925'
    abi: str = open('./assets/abi/sepolia_testnet.json', 'r').read()


@dataclass
class HemiSwapData:
    address: str = '0xA18019E62f266C2E17e33398448e4105324e0d0F'
    abi: str = open('./assets/abi/hemiswap.json', 'r').read()


@dataclass
class CapsuleData:
    address: str = '0x1E8db2Fc15Bf1207784763219e00e98D0BA82362'
    abi: str = open('./assets/abi/capsule.json', 'r').read()
