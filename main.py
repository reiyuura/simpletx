from web3 import Web3
import os
import time
import random
from dotenv import load_dotenv

load_dotenv()

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
RPC_URL = os.getenv("RPC_URL")
web3 = Web3(Web3.HTTPProvider(RPC_URL))

if not web3.is_connected():
    raise Exception("Gagal terhubung ke node RPC")
sender_address = web3.eth.account.from_key(PRIVATE_KEY).address
print(f"Alamat pengirim: {sender_address}")

chain_id = web3.eth.chain_id

#Support multiple address
RECEIVER_ADDRESSES = []

def send_transaction(to_address, amount_ether):
    print(f"[DEBUG] Mulai transaksi ke {to_address} sejumlah {amount_ether}")
    value = Web3.to_wei(amount_ether, "ether")
    nonce = web3.eth.get_transaction_count(sender_address)

    transaction = {
        "nonce": nonce,
        "to": to_address,
        "value": value,
        "gasPrice": web3.eth.gas_price,
        "chainId": chain_id,
    }
    try:
        transaction["gas"] = web3.eth.estimate_gas({
            "from": sender_address,
            "to": to_address,
            "value": value,
        })
        print(f"[DEBUG] Gas estimasi untuk {to_address}: {transaction['gas']}")
    except Exception as e:
        print(f"[ERROR] Gagal menghitung estimasi gas untuk {to_address}: {e}")
        return
    try:
        signed_tx = web3.eth.account.sign_transaction(transaction, PRIVATE_KEY)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"Transaksi dikirim ke {to_address} dengan hash: {tx_hash.hex()}")
        return tx_hash.hex()
    except Exception as e:
        print(f"[ERROR] Terjadi kesalahan saat mengirim transaksi ke {to_address}: {e}")
        return

def log_tx_hash(tx_hash, recipient):
    """
    Mencatat hash transaksi ke file log spesifik untuk setiap alamat penerima.
    """
    log_file_path = f"tx_log_{recipient}.txt"
    with open(log_file_path, "a") as log_file:
        log_file.write(f"{time.ctime()} - TX Hash: {tx_hash}\n")

def auto_transaction(interval_minutes=2):
    while True:
        try:
            recipient = random.choice(RECEIVER_ADDRESSES)
            if recipient == sender_address:
                print(f"[WARNING] Alamat penerima sama dengan pengirim. Melewatkan transaksi.")
                continue
            amount = 0.1
            print(f"Melakukan transaksi ke {recipient} dengan jumlah {amount}...")
            tx_hash = send_transaction(recipient, amount)
            if tx_hash:
                log_tx_hash(tx_hash, recipient)
                print(f"Hash transaksi: {tx_hash}")
        except Exception as e:
            print(f"[ERROR] Terjadi kesalahan saat menjalankan transaksi: {e}")
        print(f"Menunggu {interval_minutes} menit sebelum transaksi berikutnya...")
        time.sleep(interval_minutes * 60)
auto_transaction(interval_minutes=2)
