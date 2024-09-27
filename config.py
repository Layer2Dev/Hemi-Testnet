MOBILE_PROXY = False  # True - mobile proxy/False - default proxy
ROTATE_IP = False
SLIPPAGE = 0.02

PAUSE_BETWEEN_MODULES = [10, 20]
PAUSE_BETWEEN_WALLETS = [10, 20]
RETRIES = 10
PAUSE_BETWEEN_RETRIES = 60

# --- Bridges --- #
bridge_to_sepolia = False
bridge_to_hemi = False

# --- Swaps --- #
hemiswap = False

# --- Other --- #
create_capsule = False
create_safe = True

# --- Bridge config ---#


class TestnetBridgeConfig:
    from_chain = 'ARB'  # Only ARB
    to_chain = 'SEPOLIA'
    amount = 0.1
    use_percentage = True
    bridge_percentage = [0.1, 0.2]


class HemiBridgeConfig:
    from_chain = 'SEPOLIA'  # Only Sepolia
    to_chain = 'HEMI'
    amount = 0.1
    use_percentage = True
    bridge_percentage = [0.2, 0.3]


# --- Swap config --- #


class HemiSwapConfig:
    from_token = ['ETH']  # Only ETH
    to_token = ['DAI']
    amount = 0.1
    use_percentage = True
    swap_percentage = [0.01, 0.03]
    swap_all_balance = False
