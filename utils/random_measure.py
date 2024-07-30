import requests
import pathlib as pt
import os
import random
import json
from dotenv import load_dotenv

this_dir = pt.Path(__file__).parent

load_dotenv(this_dir/"postman_env")
load_dotenv(this_dir/"../.env")
import time
WILMA_URL = os.environ.get("wilma_url","http://localhost:7897")
IOTA_URL = os.environ.get("iota_north","http://localhost:14041")
WILMA_AUTH = ""
BASE_MEASURE = 20

def post_measure(device_id, measure):
    url = f"{WILMA_URL}/iot/d?k=dummykey&i={device_id}"

    payload = f"h|{measure}"
    headers = {
    'Accept': 'application/json',
    'Content-Type': 'text/plain',
    'X-Auth-Token': '7efe5a658e2ebc4830a0cde89b5917c1f3558af6'
    
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)

def get_devices():
    url = f"{IOTA_URL}/iot/devices"

    payload = ""
    headers = {
    'fiware-service': 'openiot',
    'fiware-servicepath': '/'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return json.loads(response.text)

def get_random_device(devices):
    device_names = [x["device_id"] for x in devices['devices']]
    dev_idx = random.randrange(len(device_names))
    return device_names[dev_idx]

def get_random_measure():
    rand = random.random()
    offset = 0
    if rand <0.001:
        offset = 3
    elif rand < 0.3:
        offset = 2
    elif rand < 0.7:
        offset = 1

    return BASE_MEASURE+offset


devices = get_devices()
while True:
    post_measure(get_random_device(devices),get_random_measure())
    time.sleep(1)