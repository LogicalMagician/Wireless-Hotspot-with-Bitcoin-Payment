import time
import subprocess
import webbrowser
import requests
import json

# Set up the parameters for the hotspot
ssid = "MyHotspot"
password = "MyPassword"
timeout = 60 # in minutes
price = 0.001 # in Bitcoin

# Set up the payment gateway parameters
payment_url = "https://api.commerce.coinbase.com/charges"
api_key = "YOUR_API_KEY"
api_secret = "YOUR_API_SECRET"
currency = "BTC"
metadata = {
    "description": "Wireless hotspot access"
}

# Start the hotspot
subprocess.run("netsh wlan set hostednetwork mode=allow ssid={} key={}".format(ssid, password), shell=True)
subprocess.run("netsh wlan start hostednetwork", shell=True)

# Define the function to check for payment
def check_payment():
    headers = {
        "Content-Type": "application/json",
        "X-CC-Api-Key": api_key,
        "X-CC-Version": "2018-03-22"
    }
    data = {
        "name": "Wireless hotspot access",
        "description": "Access to the wireless hotspot for {} minutes".format(timeout),
        "pricing_type": "fixed_price",
        "local_price": {
            "amount": price,
            "currency": currency
        },
        "metadata": metadata
    }
    response = requests.post(payment_url, headers=headers, data=json.dumps(data))
    response_data = json.loads(response.text)
    charge_id = response_data['data']['id']
    payment_status = response_data['data']['timeline'][0]['status']
    return charge_id, payment_status

# Check for payment every minute for the predetermined amount of time
start_time = time.time()
while (time.time() - start_time) < (timeout * 60):
    charge_id, payment_status = check_payment()
    if payment_status == "COMPLETED":
        print("Payment received. Granting access to the hotspot...")
        subprocess.run("netsh wlan stop hostednetwork", shell=True)
        subprocess.run("netsh wlan start hostednetwork", shell=True)
        break
    time.sleep(60)

# Stop the hotspot
subprocess.run("netsh wlan stop hostednetwork", shell=True)
