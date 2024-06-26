import requests
import urllib.parse
import json
import time

# URL dan headers
url = "https://api.service.gameeapp.com/"
headers = {
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Client-Language": "en",
    "Content-Type": "application/json",
    "Origin": "https://prizes.gamee.com",
    "Referer": "https://prizes.gamee.com/",
    "X-Install-Uuid": "17bfefcb-6aaa-4341-bd8b-cd3feb636513"
}

# Fungsi untuk membaca initData dari file
def read_initdata_from_file(filename):
    initdata_list = []
    with open(filename, 'r') as file:
        for line in file:
            initdata_list.append(line.strip())
    return initdata_list

# Fungsi untuk mengambil id dari initData
def get_user_id_from_init_data(init_data):
    parsed_data = urllib.parse.parse_qs(init_data)
    if 'user' in parsed_data:
        user_data = parsed_data['user'][0]
        user_data_json = urllib.parse.unquote(user_data)
        user_data_dict = json.loads(user_data_json)
        if 'id' in user_data_dict:
            return user_data_dict['id']
    return None

def get_nama_from_init_data(init_data):
    parsed_data = urllib.parse.parse_qs(init_data)
    if 'user' in parsed_data:
        user_data = parsed_data['user'][0]
        data = ""
        user_data_json = urllib.parse.unquote(user_data)
        user_data_dict = json.loads(user_data_json)
        if 'first_name' in user_data_dict:
            data = user_data_dict['first_name']
        if 'last_name' in user_data_dict:
            data = data + " " + user_data_dict['last_name']
        if 'username' in user_data_dict :
            data = data + " " + f"({user_data_dict['username']})"
    return data
# Fungsi untuk melakukan login menggunakan initData
def login_with_initdata(init_data, token):
    payload = {
        "jsonrpc": "2.0",
        "id": f"{token}",
        "method": "user.authentication.loginUsingTelegram",
        "params": {
            "initData": init_data
        }
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        # Menambahkan header Authorization dari hasil response login
        auth_token = response.json()["result"]["tokens"]["authenticate"]
        headers["Authorization"] = f"Bearer {auth_token}"
    else:
        print(f"Failed to login. Error: {response.text}")
    return response

# Fungsi untuk melakukan start session
def start_session():
    payload = {
        "jsonrpc": "2.0",
        "id": "miningEvent.startSession",
        "method": "miningEvent.startSession",
        "params": {"miningEventId": 7}
    }
    response = requests.post(url, json=payload, headers=headers)
    return response

# Fungsi untuk menjalankan operasi untuk setiap initData
def process_initdata(init_data):   
    # Login
    token = get_user_id_from_init_data(init_data)
    nama = get_nama_from_init_data(init_data)
    if token:
        login_response = login_with_initdata(init_data, token)
        if login_response.status_code == 200:
            print(f"Logged in successfully for user id: {nama}")
            
            # Start session
            start_response = start_session()
            
            if start_response.status_code == 200:
                start_data = start_response.json()
                print(f"Tiket : {start_data['user']['tickets']['count']}")
                print(f"Usd : {start_data['user']['money']['usdCents']/100}$")
                if 'error' in start_data:
                    reason = start_data['error']['data']['reason']
                    print(f"Start session error: {reason}")
                else:
                    print('Start Mining')
                    
# Main program
def main():
    initdata_file = "initdata.txt"
    
    while True:
        initdata_list = read_initdata_from_file(initdata_file)
        
        for init_data in initdata_list:
            process_initdata(init_data.strip())
            print("\n")
        
        # Delay sebelum membaca ulang file initData
        time.sleep(300)  # Delay 60 detik sebelum membaca kembali file initData

if __name__ == "__main__":
    main()
