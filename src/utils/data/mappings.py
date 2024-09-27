from src.utils.runner import *

module_handlers = {
    'bridge_to_sepolia': process_testnet_bridge,
    'bridge_to_hemi': process_hemi_bridge,
    'hemiswap': process_hemi_swap,
    'create_capsule': process_create_capsule,
    'create_safe': process_create_safe
}
