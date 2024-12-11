import os
import json

# Define base directory and other paths
base_dir = os.path.abspath("../../")
wallet_dir = os.path.join(base_dir, 'wallet')
output_sql_file = os.path.join(base_dir, 'output/import_wallet.sql')

# List to store all the SQL values
values = []

# Step 1: Read all *.address.json files
for filename in os.listdir(wallet_dir):
    if filename.endswith('-address.json'):
        # Extract wallet_name from the filename (removing the "-address.json" part)
        wallet_name = filename.split('-address.json')[0]
        file_path = os.path.join(wallet_dir, filename)
        
        # Step 2: Load the JSON content from each file
        with open(file_path, 'r') as f:
            wallet_data = json.load(f)
        
        # Step 3: Extract required fields and format them for SQL insertion
        ethereum_address = wallet_data['ethereum_address']
        private_key = wallet_data['private_key']
        public_key = wallet_data['public_key']
        pubkey_hash = wallet_data['pubkey_hash']
        
        # Step 4: Build a SQL value string
        values.append(f"('{wallet_name}', '{ethereum_address}', '{private_key}', '{public_key}', '{pubkey_hash}')")

# Step 5: Construct the full SQL query without using an f-string for multi-line strings
sql_query = (
    "INSERT INTO `wallets` (`wallet_name`, `ethereum_address`, `private_key`, `public_key`, `pubkey_hash`)\n"
    "VALUES\n" + ',\n'.join(values) + "\n"
    "ON DUPLICATE KEY UPDATE `wallet_name` = VALUES(`wallet_name`), `updated_at` = CURRENT_TIMESTAMP;"
)

# Step 6: Write the SQL query to the output file
with open(output_sql_file, 'w') as f:
    f.write(sql_query)

print(f"SQL import query with ON DUPLICATE KEY UPDATE written to {output_sql_file}")
