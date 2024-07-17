import httpx
import json

from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote

get_result = []
post_result = []

def make_request_get(url, params, client):
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = client.get(url, params=params, timeout=30.0, headers=headers)
    return response, params

def process_file_get(base_url, params_file, num_threads=5):
    global get_result
    
    result = []
    with httpx.Client() as client:
        try:
            normal_response = make_request_get(f"{base_url}'", {}, client)
            normal_len = len(normal_response[0].text)
        except Exception as e:
            print("An error occurred while trying to connect to the host!")
            return

        with open(params_file, 'r') as file:
            lines = file.read().splitlines()

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(make_request_get, f"{base_url}{quote(param)}", param, client) for param in lines]
            
            for future in futures:
                try:
                    response, param = future.result()
                    
                    if(response.status_code == 200):
                        print((normal_len), len(response.text))
                    
                        if(len(response.text) > (normal_len+(len(param)))):
                            print(f"[+] Terdapat kemungkinan Boolean Based SQL Injection dengan parameter \"{param}\" pada \"{base_url}\"")
                            result.append(f"[+] Terdapat kemungkinan Boolean Based SQL Injection dengan parameter \"{param}\" pada \"{base_url}\"")
                        
                except Exception as e:
                    print("An error occurred while processing a request:", e)
        
        if(len(result) == 0):
            print(f"[-] Tidak ditemukan kerentanan Boolean Based SQL Injection pada URL \"{base_url}\"")
        else:
            get_result += result
        
        return get_result
        
def make_request_post(url, data_value, client, param):
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = client.post(url, data=data_value, headers=headers,timeout=30.0)
    return response, param

def process_file_post(base_url, params_file, data_value, num_threads=5):
    global post_result

    result = []
    with httpx.Client() as client:
        try:
            normal_response = make_request_post(base_url, data_value, client, 'a')
            normal_len = len(normal_response[0].text)
        except Exception as e:
            print("An error occurred while trying to connect to the host!")
            return

        with open(params_file, 'r') as file:
            lines = file.read().splitlines()

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            tasks = []
            for line_number, param in enumerate(lines, start=1):
                try:
                    for key, value in data_value.items():
                        data_value[key] = quote(param)
                    
                    json_ = data_value
                    
                except json.JSONDecodeError as e:
                    print(f"Error parsing line {line_number}: {e}")
                
                tasks.append(executor.submit(make_request_post, base_url, json_, client, param))
            
            for future in tasks:
                try:
                    response, param_used = future.result()
                    
                    if(response.status_code == 200):
                        if len(response.text) > (normal_len + len(param_used)):
                            print(f"[+] Terdapat kemungkinan Boolean Based SQL Injection dengan parameter \"{param_used}\" pada \"{base_url}\"")
                            result.append(f"[+] Terdapat kemungkinan Boolean Based SQL Injection dengan parameter \"{param_used}\" pada \"{base_url}\"")
                except Exception as e:
                    print("An error occurred while processing a request:", e)
                    
        if(len(result) == 0):
            print(f"[-] Tidak ditemukan kerentanan Boolean Based SQL Injection pada URL \"{base_url}\"")
        else:
            post_result += result
        
        return post_result
        
def do_test():
    params_file = 'params/param-boolean.txt'
    file_path = 'result/result-scrape.txt'

    with open(file_path, 'r') as file:
        lines = file.readlines()

        for line_number, line in enumerate(lines, start=1):
            try:
                json_data = json.loads(line)
                method_value = json_data.get("method")
                data_value = json_data.get("data")

                if method_value == "GET":
                    url = data_value.strip()
                    process_file_get(url, params_file)
                elif method_value == "POST":
                    action_value = json_data.get("action")
                    process_file_post(action_value, params_file, data_value)

            except json.JSONDecodeError as e:
                print(f"Error parsing line {line_number}: {e}")
                
    return post_result + get_result