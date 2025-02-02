import requests
import logging
from datetime import datetime
from web3 import Web3
from eth_account import Account
import random
import time
from decimal import Decimal
import asyncio
import colorlog
import threading
from tabulate import tabulate
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Setup colored logging
formatter = colorlog.ColoredFormatter(
    '%(log_color)s%(levelname)s: %(asctime)s: %(message)s',
    log_colors={
        'DEBUG': 'green',
        'INFO': 'cyan',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white'
    },
    datefmt='%Y-%m-%d %H:%M:%S'
)

handler = colorlog.StreamHandler()
handler.setFormatter(formatter)

logger = colorlog.getLogger()
logger.addHandler(handler)
logger.setLevel(colorlog.INFO)

# Global variable to store log data for each address
address_logs = {}
log_lock = threading.Lock()

def update_log_table(address):
    """
    Function to update and display the log table for a specific address.
    """
    headers = ["Timestamp", "Status", "Trades", "Points", "Log"]
    with log_lock:
        if address in address_logs:
            print(f"\nLogs for {address}:")
            colored_table = []
            for row in address_logs[address]:
                colored_row = []
                for item in row:
                    if "Successful" in str(item) or "Complete" in str(item):  # Warna hijau untuk "Successful" dan "Complete"
                        colored_row.append(Fore.GREEN + str(item))
                    elif "Warning" in str(item) or "Retrying" in str(item):
                        colored_row.append(Fore.YELLOW + str(item))
                    elif "Error" in str(item) or "Failed" in str(item):
                        colored_row.append(Fore.RED + str(item))
                    else:
                        colored_row.append(Fore.CYAN + str(item))  # Default color for other text
                colored_table.append(colored_row)
            
            # Print the table with colored headers
            colored_headers = [Fore.CYAN + header for header in headers]
            print(tabulate(colored_table, headers=colored_headers, tablefmt="grid"))
            print("\n")  # Add some space after the table

def log_to_table(address, timestamp, status, trades, points, log):
    """
    Function to add log entry to the table for a specific address and update the display.
    """
    with log_lock:
        if address not in address_logs:
            address_logs[address] = []
        address_logs[address].append([timestamp, status, trades, points, log])
        if len(address_logs[address]) > 10:  # Limit the number of rows to keep the table manageable
            address_logs[address].pop(0)
    update_log_table(address)

def read_private_keys(file_path):
    """
    Read private keys from a file, one key per line.
    :param file_path: Path to the file containing private keys.
    :return: List of private keys.
    """
    try:
        with open(file_path, 'r') as file:
            private_keys = [line.strip() for line in file.readlines()]
        return private_keys
    except FileNotFoundError:
        raise FileNotFoundError(f"File {file_path} not found. Create a file with one private key per line.")

def generate_addresses_from_private_keys(private_keys):
    """
    Generate Ethereum addresses from private keys and save them to addresses.txt.
    :param private_keys: List of private keys.
    :return: List of Ethereum addresses.
    """
    addresses = []
    for private_key in private_keys:
        account = Account.from_key(private_key)
        addresses.append(account.address)
    
    # Save addresses to addresses.txt
    with open("addresses.txt", "w") as file:
        for address in addresses:
            file.write(address + "\n")
    
    return addresses

def read_addresses(file_path):
    """
    Read Ethereum addresses from a file, one address per line.
    :param file_path: Path to the file containing addresses.
    :return: List of Ethereum addresses.
    """
    try:
        with open(file_path, 'r') as file:
            addresses = [line.strip() for line in file.readlines()]
        return addresses
    except FileNotFoundError:
        raise FileNotFoundError(f"File {file_path} not found. Create a file with one Ethereum address per line.")

def get_random_user_agent():
    base_user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/{webkit_version} (KHTML, like Gecko) Chrome/{chrome_version} Safari/{webkit_version}",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/{webkit_version} (KHTML, like Gecko) Chrome/{chrome_version} Safari/{webkit_version}",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/{webkit_version} (KHTML, like Gecko) Chrome/{chrome_version} Safari/{webkit_version}",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/{webkit_version} (KHTML, like Gecko) Firefox/{firefox_version}",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:{firefox_version}) Gecko/20100101 Firefox/{firefox_version}",
    ]

    webkit_version = f"{random.randint(500, 600)}.{random.randint(0, 50)}"
    chrome_version = f"{random.randint(80, 100)}.0.{random.randint(4000, 5000)}.{random.randint(100, 150)}"
    firefox_version = f"{random.randint(80, 100)}.0"

    user_agent = random.choice(base_user_agents).format(
        webkit_version=webkit_version,
        chrome_version=chrome_version,
        firefox_version=firefox_version
    )

    return user_agent

headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "priority": "u=1, i",
    "sec-ch-ua": "\"Microsoft Edge\";v=\"129\", \"Not=A?Brand\";v=\"8\", \"Chromium\";v=\"129\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": get_random_user_agent()
}

def short_address(wallet_address):
    address = f"{''.join(wallet_address[:5])}..{''.join(wallet_address[-5:])}"
    return address

RPC_URL = 'https://rpc-mainnet.inichain.com'
BASE_URL = 'https://candyapi-mainnet.inichain.com/airdrop/api/v1'

# Initialize Web3
web3 = Web3(Web3.HTTPProvider(RPC_URL))
connected = web3.is_connected()
logging.info(f"Web3 connected: {connected}")

def send_testnet_eth(private_key: str, receiver_address: str, amount_in_ether: float, retries: int = 3):
    sender_address = web3.eth.account.from_key(private_key).address
    if sender_address == receiver_address:
        log_to_table(short_address(sender_address), datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "Skipping self-transfer", "N/A", "N/A", "N/A")
        return None

    amount_in_wei = web3.to_wei(amount_in_ether, 'ether')
    nonce = web3.eth.get_transaction_count(sender_address, 'pending')
    gas_price = web3.eth.gas_price

    for attempt in range(1, retries + 1):
        try:
            transaction = {
                'to': receiver_address,
                'value': amount_in_wei,
                'gas': 100000,
                'gasPrice': int(gas_price * 1.5),
                'nonce': nonce,
                'chainId': web3.eth.chain_id
            }

            signed_tx = web3.eth.account.sign_transaction(transaction, private_key)
            tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=200)

            if receipt['status'] == 1:
                log_to_table(short_address(sender_address), datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "Transfer Successful", "N/A", "N/A", tx_hash.hex())
                return tx_hash.hex()
            else:
                raise Exception(f"Transaction failed for {short_address(sender_address)}")

        except Exception as e:
            log_to_table(short_address(sender_address), datetime.now().strftime('%Y-%m-%d %H:%M:%S'), f"Error: {str(e)}", "N/A", "N/A", "N/A")
            if attempt < retries:
                gas_price = int(gas_price * 1.5)
                log_to_table(short_address(sender_address), datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "Retrying with higher gas", "N/A", "N/A", "N/A")
            else:
                log_to_table(short_address(sender_address), datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "Max retries reached", "N/A", "N/A", "N/A")
                raise e

def list_tasks(wallet_address):
    url = f"{BASE_URL}/task/list"
    headers['address'] = wallet_address
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        data = r.json()['data']
        return data

def get_user_info(wallet_address):
    url = f'{BASE_URL}/user/userInfo?address={wallet_address}'
    headers['address'] = wallet_address
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        data = r.json()["data"]
        return data

async def send_tokens(private_key, receiver_addresses):
    wallet_address = web3.eth.account.from_key(private_key).address
    abridged_address = short_address(wallet_address)

    list_tasks_data = list_tasks(wallet_address)
    day_trading_count = int(list_tasks_data['dayTradingCount'])
    trades = list_tasks_data['tasks']['dailyTask'][0]['tag']
    trade_count = int(trades.split('/')[0])
    trade_left = day_trading_count - trade_count

    for _ in range(trade_left):
        # Pilih alamat penerima secara acak dari file addresses.txt
        receiver_address = random.choice(receiver_addresses)
        try:
            points = get_user_info(wallet_address)['points']
            log_to_table(abridged_address, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "Prepping to send tokens", trades, points, "N/A")
            tx = send_testnet_eth(private_key, receiver_address, 0.000001)
            if tx:
                log_to_table(abridged_address, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "Send Token Successful", trades, points, tx)

            await asyncio.sleep(60 * 1)
            trades = list_tasks(wallet_address)['tasks']['dailyTask'][0]['tag']
        except Exception as e:
            log_to_table(abridged_address, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), f"Error: {str(e)}", trades, points, "Failed")
            await asyncio.sleep(30)

    points = get_user_info(wallet_address)['points']
    log_to_table(abridged_address, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "Trading Complete", trades, points, "Done")
    await asyncio.sleep(60 * 60 * 24)

# Function to run tasks for a single private key
def run_single_private_key(private_key, receiver_addresses):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(send_tokens(private_key, receiver_addresses))

# Run tasks for all private keys using multi-threading
def run_all(private_keys: list, receiver_addresses: list):
    threads = []
    for private_key in private_keys:
        thread = threading.Thread(target=run_single_private_key, args=(private_key, receiver_addresses))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    # Baca private keys dari file pk.txt
    private_keys = read_private_keys("pk.txt")
    
    # Generate alamat dari private keys dan simpan ke addresses.txt
    receiver_addresses = generate_addresses_from_private_keys(private_keys)
    
    # Jalankan proses pengiriman token
    run_all(private_keys, receiver_addresses)  # Berikan kedua argumen