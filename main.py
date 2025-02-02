import asyncio
import json
import logging
from utils import run_all, read_private_keys, generate_addresses_from_private_keys

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    try:
        # Load data from the JSON file (if needed for other configurations)
        with open('config.json', "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError("config.json file does not exist. Create one.")
    except json.JSONDecodeError:
        raise ValueError("The config file is not a valid JSON file.")

    # Read private keys from pk.txt
    try:
        private_keys = read_private_keys('pk.txt')
        if not private_keys:
            raise ValueError("No private keys found in pk.txt. Ensure the file contains at least one private key.")
    except FileNotFoundError:
        raise FileNotFoundError("pk.txt file does not exist. Create one with one private key per line.")

    # Generate Ethereum addresses from private keys and save them to addresses.txt
    receiver_addresses = generate_addresses_from_private_keys(private_keys)

    # Run the bot with the private keys and receiver addresses
    run_all(private_keys, receiver_addresses)

if __name__ == "__main__":
    main()