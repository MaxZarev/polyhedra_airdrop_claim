import random
import time

import requests
import json
from config import work_type, sleep_time, random_wallets

from web3 import Web3


def main():
    w3 = Web3(Web3.HTTPProvider('https://rpc.ankr.com/bsc'))

    with open('private_keys.txt', 'r') as file:
        private_keys = file.read().split('\n')

    if random_wallets == 1:
        random.shuffle(private_keys)

    for private_key in private_keys:
        if work_type == 2:
            account = w3.eth.account.from_key(private_key)
        elif work_type == 1:
            w3.eth.account.enable_unaudited_hdwallet_features()
            account = w3.eth.account.from_mnemonic(private_key)
        else:
            raise ValueError('Invalid work type')

        url = f'https://pub-88646eee386a4ddb840cfb05e7a8d8a5.r2.dev/2nd_data/{account.address[2:5].lower()}.json'  # replace this URL with the actual URL you are targeting
        response = requests.get(url)

        data = json.loads(response.text)
        for item in data:
            if item.lower() == account.address.lower():
                index = data[item]['index']
                proof = data[item]['proof']
                amount = int(data[item]['amount'], 16)
                break

        if not amount:
            print(f"{account.address}: Нет данных")
            continue

        contract = w3.eth.contract(address="0x1Eb973A834062E2abe24d5d889007508eE1213eE", abi=json.loads(open('abi.json').read()))
        data = contract.encodeABI(fn_name='claim', args=[index, account.address, amount, proof])
        dict_transaction = {
            'chainId': w3.eth.chain_id,
            'from': account.address,
            'to': contract.address,
            'data': data,
            'gas': 10000,
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.get_transaction_count(account.address),
        }
        try:
            dict_transaction['gas'] = w3.eth.estimate_gas(dict_transaction)
            signed_txn = w3.eth.account.sign_transaction(dict_transaction, private_key=account.key)
            txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            print(f"{account.address}: Клейм {amount / 10 ** 18} ZK {txn_hash.hex()}")
        except Exception as e:
            if "0x646cf558" in str(e):
                print(f"{account.address}: Ошибка: Клейм уже был сделан")
                continue
            else:
                print(f"{account.address}: Ошибка: {e}")
                continue
        finally:
            time.sleep(random.randint(*sleep_time))



if __name__ == '__main__':
    main()
