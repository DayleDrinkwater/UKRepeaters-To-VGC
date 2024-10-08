import json
import csv
import requests
from maidenhead import to_location
from geopy.distance import distance

# Requires the maidenhead and geopy libraries to be installed
# pip install maidenhead geopy

# Prompt the user for the grid locator
user_locator = input("Enter the grid locator (e.g., IO83QJ): ")


# Fetch the data from the API
api_url = "https://api-beta.rsgb.online/all/systems"
response = requests.get(api_url)
data = response.json()['data']

# Filter the data based on the specified criteria
filtered_data = [
    item for item in data 
    if item.get('modeCodes') and 'A' in item['modeCodes'] 
    and item.get('type') in ['AV', 'DM'] 
    and item.get('band') in ['2M', '70CM']
    and item.get('status') == 'OPERATIONAL'
]

# Sort the filtered data based on distance from the user's grid locator
user_location = to_location(user_locator)
filtered_data.sort(key=lambda item: distance((user_location[1], user_location[0]), (to_location(item['locator'])[1], to_location(item['locator'])[0])).km)

# Ask the user if the APRS entry should be included
aprs_entry = input("Should the APRS entry be included at position 1? (yes/no): ").strip().lower() == 'yes'

# Ask the user how many entries they wish to have (either 16 or 32)
num_entries = int(input("How many entries do you wish to have? (16 or 32): ").strip())

# Prepare the CSV file with a name based on the grid locator
csv_headers = [
    'title', 'tx_freq', 'rx_freq', 'tx_sub_audio(CTCSS=freq/DCS=number)', 
    'rx_sub_audio(CTCSS=freq/DCS=number)', 'tx_power(H/M/L)', 'bandwidth(12500/25000)', 
    'scan(0=OFF/1=ON)', 'talk around(0=OFF/1=ON)', 'pre_de_emph_bypass(0=OFF/1=ON)', 
    'sign(0=OFF/1=ON)', 'tx_dis(0=OFF/1=ON)', 'mute(0=OFF/1=ON)', 
    'rx_modulation(0=FM/1=AM)', 'tx_modulation(0=FM/1=AM)'
]

# Check if filtered data length exceeds the number of entries and print a warning if the user selected 16 entries
if num_entries == 16 and len(filtered_data) > num_entries:
    print(f"Warning: The data contains more than {num_entries} entries. The additional CSV files will need to be imported as well to add all repeaters.")

# Function to write data to a CSV file
def write_csv(file_name, data, aprs_entry):
    with open(file_name, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
        writer.writeheader()
        
        if aprs_entry:
            # Add APRS entry as the first entry if requested
            aprs_row = {
                'title': 'APRS',
                'tx_freq': '144800000',
                'rx_freq': '144800000',
                'tx_sub_audio(CTCSS=freq/DCS=number)': '',
                'rx_sub_audio(CTCSS=freq/DCS=number)': '',
                'tx_power(H/M/L)': 'H',
                'bandwidth(12500/25000)': '12500',
                'scan(0=OFF/1=ON)': '0',
                'talk around(0=OFF/1=ON)': '0',
                'pre_de_emph_bypass(0=OFF/1=ON)': '0',
                'sign(0=OFF/1=ON)': '0',
                'tx_dis(0=OFF/1=ON)': '0',
                'mute(0=OFF/1=ON)': '0',
                'rx_modulation(0=FM/1=AM)': '0',
                'tx_modulation(0=FM/1=AM)': '0'
            }
            writer.writerow(aprs_row)
        
        for item in data:  # Limit to the specified number of items
            ctcss_value = int(float(item['ctcss']) * 100)
            row = {
                'title': item['repeater'],
                'tx_freq': str(item['rx']).replace('.', ''),  # Swapped tx and rx due to repeater data -> end user radio
                'rx_freq': str(item['tx']).replace('.', ''),  # Swapped tx and rx due to repeater data -> end user radio
                'tx_sub_audio(CTCSS=freq/DCS=number)': f"{ctcss_value}",
                'rx_sub_audio(CTCSS=freq/DCS=number)': f"{ctcss_value}",
                'tx_power(H/M/L)': 'H' if item['dbwErp'] > 5 else 'L',
                'bandwidth(12500/25000)': '12500' if item['txbw'] == 12.5 else '25000',
                'scan(0=OFF/1=ON)': '1',
                'talk around(0=OFF/1=ON)': '0',
                'pre_de_emph_bypass(0=OFF/1=ON)': '0',
                'sign(0=OFF/1=ON)': '0',
                'tx_dis(0=OFF/1=ON)': '0',
                'mute(0=OFF/1=ON)': '0',
                'rx_modulation(0=FM/1=AM)': '0',
                'tx_modulation(0=FM/1=AM)': '0'
            }
            writer.writerow(row)

# Write the first CSV file
write_csv(f'Repeaters - {user_locator}.csv', filtered_data[:num_entries], aprs_entry)

# Generate additional files if needed
if num_entries == 16:
    start_index = num_entries
    end_index = start_index + num_entries
    if start_index < len(filtered_data):
        additional_csv_file = f'Repeaters - {user_locator} - Part 2.csv'
        write_csv(additional_csv_file, filtered_data[start_index:end_index], aprs_entry)