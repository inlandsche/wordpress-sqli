import httpx
import asyncio
import time
import json

from urllib.parse import quote

post_result = []
get_result = []

async def make_request_get(url, params, client):
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = await client.get(url, params=params, headers=headers, timeout=60.0)
    return response

async def make_request_post(url, data_value, client):
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = await client.post(url, data=data_value, headers=headers, timeout=60.0)
    return response

async def process_file_get(base_url, params_file):
    async with httpx.AsyncClient() as client:
        global get_result
        result = []
        
        start_normal_time = time.time()
        try:
            normal_response = await make_request_get(f"{base_url}1", {}, client) 
            elapsed_normal_time = time.time() - start_normal_time
        except:
            print("Terdapat kesalahan saat mencoba terhubung dengan host!")
            return

        with open(params_file, 'r') as file:
            lines = file.read().splitlines()

        for line_number, param in enumerate(lines, start=1):
            start_time = time.time() 
            try:
                response = await make_request_get(f"{base_url}{quote(param)}", {}, client)
                elapsed_time = time.time() - start_time

                if elapsed_time > (elapsed_normal_time + 2):
                    print(f"[+] Terdapat kemungkinan Time Based SQL Injection dengan parameter \"{param}\" pada \"{base_url}\"")
                    result.append(f"[+] Terdapat kemungkinan Time Based SQL Injection dengan parameter \"{param}\" pada \"{base_url}\"")
                
            except httpx.TimeoutException as e:
                print(f"[+] Terdapat kemungkinan Time Based SQL Injection dengan parameter \"{param}\" pada \"{base_url}\"")
                result.append(f"[+] Terdapat kemungkinan Time Based SQL Injection dengan parameter \"{param}\" pada \"{base_url}\"")
            except httpx.ConnectError as e:
                print("Terdapat error saat mencoba terhubung dengan host!")
            
        if(len(result) == 0):
            print(f"[-] Tidak ditemukan kerentanan Time Based SQL Injection pada URL \"{base_url}\"")
        else:
            get_result += result
        
        return get_result

async def process_file_post(base_url, data_value, params_file):
    async with httpx.AsyncClient() as client:
        global post_result
        result = []

        try:
            start_normal_time = time.time()
            normal_response = await make_request_post(base_url, data_value, client) 
            elapsed_normal_time = time.time() - start_normal_time
        except:
            print("Terdapat kesalahan saat mencoba terhubung dengan host!")
            return

        with open(params_file, 'r') as file:
            lines = file.read().splitlines()

        for line_number, param in enumerate(lines, start=1):
            try:
                for key, value in data_value.items():
                    data_value[key] = param
                
                json_ = data_value
                
            except json.JSONDecodeError as e:
                print(f"Error parsing line {line_number}: {e}")

            try:
                start_time = time.time() 
                response = await make_request_post(base_url, json_, client)
                elapsed_time = time.time() - start_time

                if elapsed_time > (elapsed_normal_time + 2):
                    print(f"[+] Terdapat kemungkinan Time Based SQL Injection dengan parameter \"{param}\" pada \"{base_url}\"")
                    result.append(f"[+] Terdapat kemungkinan Time Based SQL Injection dengan parameter \"{param}\" pada \"{base_url}\"")
            except httpx.TimeoutException as e:
                print(f"[+] Terdapat kemungkinan Time Based SQL Injection dengan parameter \"{param}\" pada \"{base_url}\"")
                result.append(f"[+] Terdapat kemungkinan Time Based SQL Injection dengan parameter \"{param}\" pada \"{base_url}\"")
            except httpx.ConnectError as e:
                print("Terdapat error saat mencoba terhubung dengan host!")
                
        if(len(result) == 0):
            print(f"[-] Tidak ditemukan kerentanan Time Based SQL Injection pada URL \"{base_url}\"")
        else:
            post_result += result
            
        return post_result
        
        
async def do_test():
    params_file = "params/param-time.txt"
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
                    await process_file_get(url, params_file)
                elif method_value == "POST":
                    action_value = json_data.get("action")
                    await process_file_post(action_value, data_value, params_file)

            except json.JSONDecodeError as e:
                print(f"Error parsing line {line_number}: {e}")
        
    return post_result + get_result


