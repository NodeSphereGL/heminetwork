import os
import pandas as pd
import math
from sqlalchemy import create_engine
from datetime import datetime

# Define base directory
base_dir = os.path.abspath("../../")

# Get current date and time for the file name
current_time = datetime.now().strftime('%Y%m%d_%H%M')

# Define the output Excel file with the new format
output_excel_file = os.path.join(base_dir, f'output/faucet_{current_time}.xlsx')

# Step 1: Use SQLAlchemy for the database connection
db_url = "mysql+mysqlconnector://root:123123@127.0.0.1/hemi_network"
engine = create_engine(db_url)

try:
    # Step 2: Query profiles and wallets
    profile_query = "SELECT profile_name, discord_username, discord_password, discord_2fa FROM profiles WHERE is_active = 1"
    
    # Updated wallet query to order by balance and wallet_name in ascending order
    wallet_query = "SELECT wallet_name, pubkey_hash FROM wallets ORDER BY balance ASC, wallet_name ASC"
    
    profiles_df = pd.read_sql(profile_query, engine)
    wallets_df = pd.read_sql(wallet_query, engine)
    
    X = len(profiles_df)  # Number of profiles (150)
    Y = len(wallets_df)  # Number of wallets (500)

    # Step 3: Calculate total sheets required and number of wallets per sheet
    profiles_per_sheet = X  # Fixed: 150 profiles per sheet
    total_sheets = math.ceil(Y / profiles_per_sheet)  # Calculate total sheets needed
    wallets_per_sheet = profiles_per_sheet  # Each sheet has 150 profiles, so 150 wallets should go per sheet (until the last)

    # Step 4: No wallet shuffling, they will be ordered by balance (as per the query)
    writer = pd.ExcelWriter(output_excel_file, engine='xlsxwriter')

    for sheet_num in range(1, total_sheets + 1):
        start_idx_wallet = (sheet_num - 1) * wallets_per_sheet

        if sheet_num == total_sheets:
            # The last sheet gets the remaining wallets
            end_idx_wallet = Y
        else:
            end_idx_wallet = start_idx_wallet + wallets_per_sheet

        # Get the wallets for this sheet
        sheet_wallets = wallets_df[start_idx_wallet:end_idx_wallet].reset_index(drop=True)

        # Repeat profiles if needed, for the current sheet
        sheet_profiles = profiles_df.head(len(sheet_wallets)).copy()  # Make an explicit copy to avoid the warning

        # Add wallet_name and pubkey_hash to the profiles using .loc[] to avoid the SettingWithCopyWarning
        sheet_profiles.loc[:, 'wallet_name'] = sheet_wallets['wallet_name']  # Add wallet_name to column E
        sheet_profiles.loc[:, 'pubkey_hash'] = sheet_wallets['pubkey_hash']  # Add pubkey_hash to column F

        # Write this dataframe to the corresponding sheet
        sheet_name = f'Sheet{sheet_num}'
        sheet_profiles.to_excel(writer, sheet_name=sheet_name, index=False, 
                                columns=['profile_name', 'discord_username', 'discord_password', 'discord_2fa', 'wallet_name', 'pubkey_hash'])

        # Set the column width to 30 for all columns
        worksheet = writer.sheets[sheet_name]  # Access the sheet by its name
        worksheet.set_column('A:F', 30)  # Set width for columns A to F to 30

    # Step 5: Close the Excel writer
    writer.close()
    print(f"Excel file saved to {output_excel_file} with wallets ordered by balance.")

except Exception as e:
    print(f"Error: {e}")
