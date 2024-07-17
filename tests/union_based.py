import httpx
import json

get_result = []
post_result = []

def make_request_get(url, params, client):
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = client.get(url, params=params, timeout=30.0, headers=headers)
    return response, params

def process_file_get(base_url, params_file):
    global get_result
    result = []
    with httpx.Client() as client:
        try:
            normal_response = make_request_get(f"{base_url}1", {}, client)
            normal_len = len(normal_response[0].text)
        except Exception as e:
            print("An error occurred while trying to connect to the host!")
            return

        with open(params_file, 'r') as file:
            lines = file.read().splitlines()

            for line_number, param in enumerate(lines, start=1):
                try:
                    response = make_request_get(f"{base_url}{param}", {}, client)[0]
                    
                    if((len(response.text) > (normal_len+len(param))) and "b7adfyshdsjconcated" in response.text):
                        print(f"[+] Terdapat kemungkinan Union Based SQL Injection dengan parameter \"{param}\" pada \"{base_url}\"")
                        # print("Parameter: {} bisa mendeteksi kerentanan pada {}".format(param, base_url))
                        result.append(f"[+] Terdapat kemungkinan Union Based SQL Injection dengan parameter \"{param}\" pada \"{base_url}\"")
                    # else:
                    #     print("Parameter: {} tidak bisa mendeteksi kerentanan pada {}".format(param, base_url))
        
                except Exception as e:
                    print("An error occurred while processing a request:", e)
        
        if(len(result) == 0):
            print(f"[-] Tidak ditemukan kerentanan Union Based SQL Injection pada URL \"{base_url}\"")
        else:
            get_result += result
        
        return get_result
          
def make_request_post(url, data_value, client, param):
    header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate, br", "Content-Type": "application/x-www-form-urlencoded", "Origin": "http://103.127.135.93:8080", "Connection": "close", "Referer": "http://103.127.135.93:8080/", "Upgrade-Insecure-Requests": "1"}
    response = client.post(url, data=data_value, headers=header, timeout=30.0)
    return response, param

def process_file_post(base_url, params_file, data_value):
    global post_result
    result = []
    with httpx.Client() as client:
        try:
            normal_response, normal_param = make_request_post(base_url, data_value, client, 'normal')
            normal_len = len(normal_response.text)
        except Exception as e:
            print("An error occurred while trying to connect to the host!")
            print(e)
            return

        with open(params_file, 'r') as file:
            lines = file.read().splitlines()
            
            for line_number, param in enumerate(lines, start=1):
                try:
                    for key, value in data_value.items():
                        data_value[key] = param
                    
                    
                except json.JSONDecodeError as e:
                    print(f"Error parsing line {line_number}: {e}")
                    
                response = make_request_post(base_url, data_value, client, data_value)[0]
                
                if((len(response.text) > (normal_len+len(param))) and "b7adfyshdsjconcated" in response.text):
                    print(f"[+] Terdapat kemungkinan Union Based SQL Injection dengan parameter \"{param}\" pada \"{base_url}\"")
                    # print("Parameter: {} bisa mendeteksi kerentanan pada {}".format(param, base_url))

                    result.append(f"[+] Terdapat kemungkinan Union Based SQL Injection dengan parameter \"{param}\" pada \"{base_url}\"")
                # else:
                #     print("Parameter: {} tidak bisa mendeteksi kerentanan pada {}".format(param, base_url))
                    
        if(len(result) == 0):
            print(f"[-] Tidak ditemukan kerentanan Union Based SQL Injection pada URL \"{base_url}\"")
        else:
            post_result += result
         
        return post_result

def do_test():
    params_file = 'params/param-union.txt'
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
        
        result = get_result + post_result

    return result