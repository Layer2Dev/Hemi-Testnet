from colorama import Fore

from src.utils.data.mappings import module_handlers

with open('config.py', 'r', encoding='utf-8-sig') as file:
    module_config = file.read()

exec(module_config)

with open('wallets.txt', 'r', encoding='utf-8-sig') as file:
    private_keys = [line.strip() for line in file]

with open('proxies.txt', 'r', encoding='utf-8-sig') as file:
    proxies = [line.strip() for line in file]
    if not proxies:
        proxies = [None for _ in range(len(private_keys))]

patterns = {}

for module in module_handlers:
    if globals().get(module):
        patterns[module] = 'On'
    else:
        patterns[module] = 'Off'

print(Fore.BLUE + f'Loaded {len(private_keys)} wallets:')
print('\033[39m')

print(f'----------------------------------------Modules--------------------------------------------')

for pattern, value in patterns.items():
    if value == 'Off':
        print("\033[31m {}".format(f'{pattern} = {value}'))
    else:
        print("\033[32m {}".format(f'{pattern} = {value}'))
print('\033[39m')

active_module = [module for module, value in patterns.items() if value == 'On']
