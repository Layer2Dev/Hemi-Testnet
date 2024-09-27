from loguru import logger

from config import *
from src.modules.bridge.bridge_factory import HemiBridge, SepoliaBridge
from src.modules.capsule.create_capsule import Capsule
from src.modules.safe.create_safe import GnosisSafe
from src.modules.swap.swap_factory import HemiSwap
from src.models.bridge import BridgeConfig
from src.models.chain import Chain
from src.models.token import Token

from src.utils.data.chains import chain_mapping
from src.utils.proxy_manager import Proxy


async def process_create_safe(private_key: str, proxy: Proxy | None) -> None:
    safe = GnosisSafe(
        private_key=private_key,
        proxy=proxy
    )
    logger.debug(safe)
    await safe.create_safe()


async def process_testnet_bridge(private_key: str, proxy: Proxy | None) -> None:
    from_chain = TestnetBridgeConfig.from_chain
    to_chain = TestnetBridgeConfig.to_chain
    amount = TestnetBridgeConfig.amount
    use_percentage = TestnetBridgeConfig.use_percentage
    bridge_percentage = TestnetBridgeConfig.bridge_percentage

    sepolia = SepoliaBridge(
        private_key=private_key,
        proxy=proxy,
        bridge_config=BridgeConfig(
            from_chain=Chain(
                chain_name=from_chain,
                native_token=chain_mapping[from_chain.upper()].native_token,
                rpc=chain_mapping[from_chain.upper()].rpc,
                chain_id=chain_mapping[from_chain.upper()].chain_id
            ),
            to_chain=Chain(
                chain_name=to_chain,
                native_token=chain_mapping[to_chain.upper()].native_token,
                rpc=chain_mapping[to_chain.upper()].rpc,
                chain_id=chain_mapping[to_chain.upper()].chain_id
            ),
            from_token=Token(
                chain_name=from_chain,
                name='ETH',
            ),
            to_token=Token(
                chain_name=to_chain,
                name='ETH',
            ),
            amount=amount,
            use_percentage=use_percentage,
            bridge_percentage=bridge_percentage
        )
    )

    logger.debug(sepolia)
    await sepolia.bridge()


async def process_hemi_bridge(private_key: str, proxy: Proxy | None) -> None:
    from_chain = HemiBridgeConfig.from_chain
    amount = HemiBridgeConfig.amount
    use_percentage = HemiBridgeConfig.use_percentage
    bridge_percentage = HemiBridgeConfig.bridge_percentage

    hemi_bridge = HemiBridge(
        private_key=private_key,
        proxy=proxy,
        bridge_config=BridgeConfig(
            from_chain=Chain(
                chain_name=from_chain,
                native_token=chain_mapping[from_chain.upper()].native_token,
                rpc=chain_mapping[from_chain.upper()].rpc,
                chain_id=chain_mapping[from_chain.upper()].chain_id
            ),
            to_chain=Chain(
                chain_name='HEMI',
                native_token=chain_mapping['HEMI'].native_token,
                rpc=chain_mapping['HEMI'].rpc,
                chain_id=chain_mapping['HEMI'].chain_id
            ),
            from_token=Token(
                chain_name=from_chain,
                name='ETH',
            ),
            to_token=Token(
                chain_name='HEMI',
                name='ETH',
            ),
            amount=amount,
            use_percentage=use_percentage,
            bridge_percentage=bridge_percentage
        )
    )
    logger.debug(hemi_bridge)
    await hemi_bridge.bridge()


async def process_hemi_swap(private_key: str, proxy: Proxy | None) -> None:
    from_token = HemiSwapConfig.from_token
    to_token = HemiSwapConfig.to_token
    amount = HemiSwapConfig.amount
    use_percentage = HemiSwapConfig.use_percentage
    swap_percentage = HemiSwapConfig.swap_percentage
    swap_all_balance = HemiSwapConfig.swap_all_balance

    hemiswap = HemiSwap(
        private_key=private_key,
        from_token=from_token,
        to_token=to_token,
        amount=amount,
        use_percentage=use_percentage,
        swap_percentage=swap_percentage,
        swap_all_balance=swap_all_balance,
        proxy=proxy,
    )
    logger.debug(hemiswap)
    await hemiswap.swap()


async def process_create_capsule(private_key: str, proxy: Proxy | None) -> None:
    capsule = Capsule(
        private_key=private_key,
        proxy=proxy
    )
    logger.debug(capsule)
    await capsule.create_capsule()
