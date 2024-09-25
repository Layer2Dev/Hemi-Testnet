MOBILE_PROXY = False  # True - mobile proxy/False - default proxy
ROTATE_IP = False
SLIPPAGE = 0.02

PAUSE_BETWEEN_MODULES = [10, 20]
PAUSE_BETWEEN_WALLETS = [10, 20]
RETRIES = 3
PAUSE_BETWEEN_RETRIES = 1

# --- Bridges --- #
bridge_to_sepolia = True
bridge_to_hemi = True

# --- Swaps --- #
hemiswap = True

# --- Other --- #
create_capsule = True


# --- Bridge config ---#


class TestnetBridgeConfig:
    from_chain = 'ARB'  # Only ARB
    to_chain = 'SEPOLIA'
    amount = 0.1
    use_percentage = True
    bridge_percentage = [0.1, 0.2]


class HemiBridgeConfig:
    from_chain = 'SEPOLIA'
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
