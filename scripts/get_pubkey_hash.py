import os
import json
import re

def get_pubkey_hash():
    base_dir = os.path.abspath("../")
    wallet_dir = os.path.join(base_dir, "wallet")
    output_dir = os.path.join(base_dir, "output")

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    pubkey_file_path = os.path.join(output_dir, "pubkey_hash.txt")
    pubkey_discord_file_path = os.path.join(output_dir, "pubkey_hash_discord.txt")

    # Step 1: Remove old pubkey_hash.txt and pubkey_hash_discord.txt if they exist
    if os.path.exists(pubkey_file_path):
        os.remove(pubkey_file_path)
        print(f"Old pubkey_hash.txt file removed.")

    if os.path.exists(pubkey_discord_file_path):
        os.remove(pubkey_discord_file_path)
        print(f"Old pubkey_hash_discord.txt file removed.")

    # Step 2: Iterate over all JSON files in the wallet directory
    pubkey_entries = []
    for filename in os.listdir(wallet_dir):
        if filename.endswith("-address.json"):
            match = re.match(r"popm(\d{3})-address\.json", filename)
            if match:
                wallet_number = int(match.group(1))  # Convert to integer for sorting
                wallet_path = os.path.join(wallet_dir, filename)

                # Load JSON file content
                with open(wallet_path, 'r') as wallet_file:
                    wallet_data = json.load(wallet_file)
                
                # Extract pubkey_hash
                pubkey_hash = wallet_data.get("pubkey_hash")
                if pubkey_hash:
                    pubkey_entries.append((wallet_number, pubkey_hash))

    # Step 3: Sort entries by wallet number in ascending order
    pubkey_entries.sort(key=lambda x: x[0])

    # Step 4: Write all pubkey_hash entries into pubkey_hash.txt
    with open(pubkey_file_path, 'w') as pubkey_file:
        for wallet_number, pubkey_hash in pubkey_entries:
            pubkey_file.write(f"{wallet_number:03d}|{pubkey_hash}\n")
    
    print(f"New pubkey_hash.txt file created with {len(pubkey_entries)} entries.")

    # Step 5: Write pubkey hashes only into pubkey_hash_discord.txt in the same order
    with open(pubkey_discord_file_path, 'w') as pubkey_discord_file:
        pubkey_only_entries = [entry[1] for entry in pubkey_entries]  # Extract sorted pubkey_hash values
        pubkey_discord_file.write("\n".join(pubkey_only_entries))
    
    print(f"New pubkey_hash_discord.txt file created with {len(pubkey_only_entries)} entries.")

if __name__ == "__main__":
    get_pubkey_hash()
