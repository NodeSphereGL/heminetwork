import subprocess
import json
import os
import re
from datetime import datetime
import shutil

def get_highest_wallet_number(wallet_dir):
    max_number = 0
    for filename in os.listdir(wallet_dir):
        match = re.match(r"popm(\d{3})-address\.json", filename)
        if match:
            number = int(match.group(1))
            if number > max_number:
                max_number = number
    return max_number

def create_wallets(num_wallets):
    base_dir = os.path.abspath("../")
    wallet_dir = os.path.join(base_dir, "wallet")
    docker_dir = os.path.join(base_dir, "hemi_docker")
    env_file_path = os.path.join(docker_dir, ".env")
    docker_compose_path = os.path.join(docker_dir, "docker-compose.yml")

    # Get the parent directory name (e.g., 'node01')
    node_name = os.path.basename(os.path.dirname(docker_dir))
    network_name = f"network-{node_name}"

    # Step 1: Backup .env and docker-compose.yml
    timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
    env_backup_path = f"{env_file_path}.bak.{timestamp}"
    docker_compose_backup_path = f"{docker_compose_path}.bak.{timestamp}"

    shutil.copy(env_file_path, env_backup_path)
    shutil.copy(docker_compose_path, docker_compose_backup_path)

    print(f"Backup created: {env_backup_path}")
    print(f"Backup created: {docker_compose_backup_path}")

    # Step 2: Determine the highest numbered wallet and start from there
    highest_wallet_number = get_highest_wallet_number(wallet_dir)
    start_number = highest_wallet_number + 1

    # Step 3: Add one-time comment to .env and docker-compose.yml before adding new entries
    env_comment = f"\n#\n# Create new {num_wallets} private keys starting from {start_number:03d} on {timestamp}\n#\n"
    docker_comment = f"\n#\n# Create new {num_wallets} services starting from {start_number:03d} on {timestamp}\n#\n"

    with open(env_file_path, 'a') as env_file:
        env_file.write(env_comment)

    with open(docker_compose_path, 'a') as docker_compose_file:
        docker_compose_file.write(docker_comment)

    # Step 4: Check if networks section exists and add it if not
    """
    with open(docker_compose_path, 'r+') as docker_compose_file:
        docker_compose_content = docker_compose_file.read()
        if 'networks:' not in docker_compose_content:
            docker_compose_file.write(f"\nnetworks:\n  {network_name}:\n    driver: bridge\n")
    """

    # Step 5: Create wallets and update files
    for i in range(start_number, start_number + num_wallets):
        wallet_filename = f"popm{i:03d}-address.json"
        wallet_path = os.path.join(wallet_dir, wallet_filename)

        # Check if the wallet file already exists
        if not os.path.exists(wallet_path):
            print(f"Creating wallet: {wallet_filename}")
            
            # Run keygen command to create the wallet
            command = f"./bin/keygen -secp256k1 -json -net=\"testnet\" > {wallet_path}"
            subprocess.run(command, shell=True, cwd=base_dir)
        else:
            print(f"Wallet {wallet_filename} already exists, skipping keygen.")

        # Load wallet data
        with open(wallet_path, 'r') as wallet_file:
            wallet_data = json.load(wallet_file)

        # Add private key to .env file
        private_key = wallet_data["private_key"]
        env_entry = f"POPM_BTC_PRIVKEY_{i:03d}={private_key}\n"
        with open(env_file_path, 'a') as env_file:
            env_file.write(env_entry)

        # Update docker-compose.yml with the service definition
        docker_service_entry = f"""
  popmd{i:03d}_{node_name}:
    image: toanbk/heminetwork:latest
    environment:
      - POPM_BTC_PRIVKEY=${{POPM_BTC_PRIVKEY_{i:03d}}}
      - POPM_STATIC_FEE=${{POPM_STATIC_FEE}}
      - http_proxy=${{PROXY_{i:03d}}}
      - HTTP_PROXY=${{PROXY_{i:03d}}}
      - https_proxy=${{PROXY_{i:03d}}}
      - HTTPS_PROXY=${{PROXY_{i:03d}}}
      - no_proxy=${{NO_PROXY}}
      - NO_PROXY=${{NO_PROXY}}
    networks:
      - {network_name}
    restart: always
"""
        with open(docker_compose_path, 'a') as docker_compose_file:
            docker_compose_file.write(docker_service_entry)

if __name__ == "__main__":
    num_wallets = int(input("Enter the number of wallets to create: "))
    create_wallets(num_wallets)
