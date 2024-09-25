class Chain:
    def __init__(self, chain_id: int, rpc: str, scan: str, native_token: str) -> None:
        self.chain_id = chain_id
        self.rpc = rpc
        self.scan = scan
        self.native_token = native_token


ETH = Chain(
    chain_id=1,
    rpc='https://rpc.ankr.com/eth',
    scan='https://etherscan.io/tx',
    native_token='ETH',
)


ARB = Chain(
    chain_id=42161,
    rpc='https://arb1.arbitrum.io/rpc',
    scan='https://arbiscan.io/tx',
    native_token='ETH',
)


OP = Chain(
    chain_id=10,
    rpc='https://op-pokt.nodies.app',
    scan='https://optimistic.etherscan.io/tx',
    native_token='ETH',
)


SEPOLIA = Chain(
    chain_id=11155111,
    rpc='https://ethereum-sepolia-rpc.publicnode.com',
    scan='https://sepolia.etherscan.io/tx',
    native_token='ETH' # sETH
)

HEMI = Chain(
    chain_id=743111,
    rpc='https://testnet.rpc.hemi.network/rpc',
    scan='https://testnet.explorer.hemi.xyz/tx',
    native_token='ETH'
)

chain_mapping = {
    'ETH': ETH,
    'ARB': ARB,
    'OP': OP,
    'SEPOLIA': SEPOLIA,
    'HEMI': HEMI
}
