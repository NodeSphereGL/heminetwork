import os;
import requests
import threading
import mysql.connector
from queue import Queue

table_name = "wallets"
base_dir = os.path.abspath("../")
proxy_list_path = os.path.join(base_dir, "proxy", "list.txt")

# Get database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",  # replace with your DB host
        user="root",  # replace with your DB user
        password="123123",  # replace with your DB password
        database="hemi_network"  # replace with your database name
    )

# Fetch all pubkey_hash from the wallets table
def get_pubkey_hashes():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(f"SELECT pubkey_hash FROM {table_name}")
    pubkey_hashes = cursor.fetchall()
    connection.close()
    return [row[0] for row in pubkey_hashes]

# Read proxies from the file proxy/list.txt
def get_proxies():
    proxies = []
    with open(proxy_list_path, 'r') as file:
        for line in file:
            domain, port, username, password = line.strip().split(':')
            proxy = {
                'http': f'http://{username}:{password}@{domain}:{port}',
                'https': f'https://{username}:{password}@{domain}:{port}'
            }
            proxies.append(proxy)
    return proxies

# Update wallet's tx_count and balance
def update_wallet(pubkey_hash, proxy):
    try:
        # Call API to get wallet information
        url = f"https://blockstream.info/testnet/api/address/{pubkey_hash}"
        response = requests.get(url, proxies=proxy, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            chain_stats = data['chain_stats']
            tx_count = chain_stats['tx_count']
            balance = chain_stats['funded_txo_sum'] - chain_stats['spent_txo_sum']

            if tx_count == 0:
                print(f"Wallet {pubkey_hash}: tx_count={tx_count}, balance={balance}, nothing to update ...")
                return
            
            # Update the database with tx_count and balance
            connection = get_db_connection()
            cursor = connection.cursor()
            query = f"UPDATE {table_name} SET tx_count = %s, balance = %s WHERE pubkey_hash = %s"
            cursor.execute(query, (tx_count, balance, pubkey_hash))
            
            connection.commit()
            connection.close()
            print(f"Updated wallet {pubkey_hash}: tx_count={tx_count}, balance={balance}")
        else:
            print(f"Failed to fetch data for {pubkey_hash}, Status Code: {response.status_code}")
    
    except Exception as e:
        print(f"Error for {pubkey_hash}: {e}")

# Worker function for multithreading
def worker(q, proxies):
    while not q.empty():
        pubkey_hash = q.get()
        proxy = proxies[q.qsize() % len(proxies)]  # Assign proxy in round-robin fashion
        update_wallet(pubkey_hash, proxy)
        q.task_done()

# Main function to execute the logic
def main():
    # Get pubkey_hashes from the database
    pubkey_hashes = get_pubkey_hashes()
    
    # Get proxy list from file
    proxies = get_proxies()

    # Create a queue for pubkey_hashes
    q = Queue()
    for pubkey_hash in pubkey_hashes:
        q.put(pubkey_hash)

    # Create 10 threads for parallel requests
    threads = []
    for _ in range(100):
        t = threading.Thread(target=worker, args=(q, proxies))
        t.start()
        threads.append(t)
    
    # Wait for the queue to be processed
    q.join()

    # Ensure all threads complete their work
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
