from web3 import Web3
import os
from dotenv import load_dotenv
import time

load_dotenv()

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
RPC_URL = os.getenv("RPC_URL")
PENERIMA = os.getenv("RECEIPT_ADDRESS")

web3 = Web3(Web3.HTTPProvider(RPC_URL))

if not web3.is_connected():
    raise Exception("Gagal terhubung ke node RPC")
sender_address = web3.eth.account.from_key(PRIVATE_KEY).address
print(f"Alamat pengirim: {sender_address}")
chain_id = web3.eth.chain_id
def send_transaction(to_address, amount_ether):
    value = Web3.to_wei(amount_ether, "ether")
    nonce = web3.eth.get_transaction_count(sender_address)

    transaction = {
        "nonce": nonce,
        "to": to_address,
        "value": value,
        "gasPrice": web3.eth.gas_price,
        "chainId": chain_id,
    }
    transaction["gas"] = web3.eth.estimate_gas({
        "from": sender_address,
        "to": to_address,
        "value": value,
    })

    try:
        signed_tx = web3.eth.account.sign_transaction(transaction, PRIVATE_KEY)
    except Exception as e:
        print(f"Terjadi kesalahan saat menandatangani transaksi: {e}")
        return
    try:
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"Transaksi dikirim dengan hash: {tx_hash.hex()}")
        return tx_hash.hex()
    except Exception as e:
        print(f"Terjadi kesalahan saat mengirim transaksi: {e}")
        return

def log_tx_hash(tx_hash):
    log_file_path = "tx_hash_log.txt"
    if os.path.exists(log_file_path):
        with open(log_file_path, "r") as log_file:
            lines = log_file.readlines()
        if len(lines) >= 50:
            lines = lines[1:]
        with open(log_file_path, "w") as log_file:
            log_file.writelines(lines)
            log_file.write(f"{time.ctime()} - TX Hash: {tx_hash}\n")
    else:
        with open(log_file_path, "w") as log_file:
            log_file.write(f"{time.ctime()} - TX Hash: {tx_hash}\n")

def auto_transaction(interval_minutes=5):
    while True:
        try:
            recipient = PENERIMA
            amount = 0.01  # Jumlah token yang dikirim
            print(f"Melakukan transaksi ke {recipient} dengan jumlah {amount} INI...")
            tx_hash = send_transaction(recipient, amount)
            if tx_hash:
                log_tx_hash(tx_hash)
                print(f"Hash transaksi: {tx_hash}")
        except Exception as e:
            print(f"Terjadi kesalahan saat menjalankan transaksi: {e}")
        print(f"Menunggu {interval_minutes} menit sebelum transaksi berikutnya...")
        time.sleep(interval_minutes * 60)
auto_transaction(interval_minutes=5)