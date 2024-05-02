import requests
import json

# Define the server address here
server_addr = 'http://192.168.137.177:5000'

latitude = float(input("Enter the bin's location:\nLatitude: "))
longitude = float(input("Longitude: "))
bin_height = float(input("Enter the bin's height: "))
bin_capacity = float(input("Enter the bin's capacity: "))

data = {
    'latitude': latitude,
    'longitude': longitude,
    'bin_height': bin_height,
    'bin_capacity': bin_capacity
}

response = requests.post(f'{server_addr}/new_connection', json=data)
response_data = response.json()

print(f"Response from server: {response.text}")

if response_data['status']=='success':
    print(f"bin_id = {response_data['bin_id']}")
    data['bin_id'] = response_data['bin_id']
    with open('bin_details.json', 'w') as f:
        json.dump(data, f)
else:
    print(response_data['message'])