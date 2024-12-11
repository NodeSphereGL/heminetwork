import os
import re

def update_proxy_env():
    base_dir = os.path.abspath("../")
    proxy_list_path = os.path.join(base_dir, "proxy", "list.txt")
    wallet_dir = os.path.join(base_dir, "wallet")
    env_file_path = os.path.join(base_dir, "hemi_docker", ".env")
    output_file_path = os.path.join(base_dir, "output", "proxy.txt")

    # Step 1: Read proxy list from list.txt
    try:
        with open(proxy_list_path, 'r') as proxy_file:
            proxy_lines = proxy_file.readlines()
    except FileNotFoundError:
        print(f"Error: Proxy list file not found at {proxy_list_path}")
        return

    formatted_proxies = []
    
    # Step 2: Format the proxy lines
    for line in proxy_lines:
        line = line.strip()
        if line:
            parts = line.split(':')
            if len(parts) == 4:
                ip, port, user, password = parts
                formatted_proxy = f"http://{user}:{password}@{ip}:{port}"
                formatted_proxies.append(formatted_proxy)
            else:
                print(f"Error: Invalid proxy format in line: {line}")
    
    if not formatted_proxies:
        print("Error: No valid proxies found.")
        return

    # Step 3: Get wallet numbers from JSON filenames
    wallet_files = [f for f in os.listdir(wallet_dir) if f.endswith('-address.json')]
    wallet_numbers = []
    
    for filename in wallet_files:
        match = re.match(r"popm(\d{3})-address\.json", filename)
        if match:
            wallet_number = match.group(1)
            wallet_numbers.append(wallet_number)
    
    if not wallet_numbers:
        print("Error: No wallet files found.")
        return

    # Step 4: Ensure proxies match wallets by repeating the proxy list if necessary
    if len(formatted_proxies) < len(wallet_numbers):
        print(f"Warning: Not enough proxies. Repeating the proxy list to match wallet files.")
        formatted_proxies *= (len(wallet_numbers) // len(formatted_proxies)) + 1
        formatted_proxies = formatted_proxies[:len(wallet_numbers)]  # Trim to the exact number of wallet files

    # Step 5: Sort wallet numbers in ascending order
    wallet_numbers.sort()

    # Step 6: Read current .env file and remove old PROXY_xxx entries
    if os.path.exists(env_file_path):
        with open(env_file_path, 'r') as env_file:
            env_lines = env_file.readlines()
    else:
        env_lines = []

    new_env_lines = [line for line in env_lines if not re.match(r"PROXY_\d{3}=", line)]

    # Step 7: Add new PROXY_xxx entries for each wallet
    proxy_assignments = []
    for wallet_number, proxy in zip(wallet_numbers, formatted_proxies):
        new_env_lines.append(f"PROXY_{wallet_number}={proxy}\n")
        proxy_assignments.append(f"PROXY_{wallet_number}|{proxy}")
        print(f"Added/Updated: PROXY_{wallet_number}={proxy}")

    # Step 8: Write updated .env file
    try:
        with open(env_file_path, 'w') as env_file:
            env_file.writelines(new_env_lines)
        print(f".env file updated successfully.")
    except Exception as e:
        print(f"Error: Unable to write to .env file: {e}")

    # Step 9: Write proxy assignments to proxy.txt
    try:
        os.makedirs(os.path.join(base_dir, "output"), exist_ok=True)  # Ensure output directory exists
        with open(output_file_path, 'w') as output_file:
            output_file.write("\n".join(proxy_assignments) + "\n")
        print(f"Proxy assignments written to {output_file_path}.")
    except Exception as e:
        print(f"Error: Unable to write to {output_file_path}: {e}")

if __name__ == "__main__":
    update_proxy_env()
