import json
import csv
import requests

# Prompt the user for the grid locator
grid_locator = input("Enter the grid locator (e.g., IO83): ")

# Fetch the data from the API
api_url = f"https://api-beta.rsgb.online/locator/{grid_locator}"
response = requests.get(api_url)
data = response.json()['data']

# Debug: Print the raw data fetched from the API
print("Raw data fetched from the API:")
print(json.dumps(data, indent=2))

# Debug: Print the structure of a few items in the raw data
if data:
    print("Structure of the first item in the raw data:")
    print(json.dumps(data[0], indent=2))

# Filter the data based on the specified criteria
filtered_data = [
    item for item in data 
    if item.get('modeCodes') and 'A' in item['modeCodes'] 
    and item.get('type') == 'AV' 
    and item.get('band') in ['2M', '70CM']
    and item.get('status') != 'NOT OPERATIONAL'
]

# Debug: Print the filtered data
print("Filtered data:")
print(json.dumps(filtered_data, indent=2))

# Prepare the CSV file with a name based on the grid locator
csv_file = f'Repeaters - {grid_locator}.csv'
csv_headers = [
    'title', 'tx_freq', 'rx_freq', 'tx_sub_audio(CTCSS=freq/DCS=number)', 
    'rx_sub_audio(CTCSS=freq/DCS=number)', 'tx_power(H/M/L)', 'bandwidth(12500/25000)', 
    'scan(0=OFF/1=ON)', 'talk around(0=OFF/1=ON)', 'pre_de_emph_bypass(0=OFF/1=ON)', 
    'sign(0=OFF/1=ON)', 'tx_dis(0=OFF/1=ON)', 'mute(0=OFF/1=ON)', 
    'rx_modulation(0=FM/1=AM)', 'tx_modulation(0=FM/1=AM)'
]

# Check if filtered data length exceeds 32 and print a warning
if len(filtered_data) > 32:
    print("Warning: The data contains more than 32 entries. Only the first 32 will be written to the CSV file.")

# Transform and write the filtered data to CSV
with open(csv_file, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
    writer.writeheader()
    
    for item in filtered_data[:32]:  # Limit to the first 32 items
        ctcss_value = int(float(item['ctcss']) * 100)
        row = {
            'title': item['repeater'],
            'tx_freq': str(item['tx']).replace('.', ''),
            'rx_freq': str(item['rx']).replace('.', ''),
            'tx_sub_audio(CTCSS=freq/DCS=number)': f"{ctcss_value}",
            'rx_sub_audio(CTCSS=freq/DCS=number)': f"{ctcss_value}",
            'tx_power(H/M/L)': 'H' if item['dbwErp'] > 5 else 'L',
            'bandwidth(12500/25000)': '12500' if item['txbw'] == 12.5 else '25000',
            'scan(0=OFF/1=ON)': '0',
            'talk around(0=OFF/1=ON)': '0',
            'pre_de_emph_bypass(0=OFF/1=ON)': '0',
            'sign(0=OFF/1=ON)': '0',
            'tx_dis(0=OFF/1=ON)': '0',
            'mute(0=OFF/1=ON)': '0',
            'rx_modulation(0=FM/1=AM)': '0',
            'tx_modulation(0=FM/1=AM)': '0'
        }
        writer.writerow(row)