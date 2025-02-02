import requests
import re
import json

from urllib.parse import urlparse, urlunparse
from bs4 import BeautifulSoup

def get_base_url(url):
    parsed_url = urlparse(url)
    base_url = urlunparse((parsed_url.scheme, parsed_url.netloc, '', '', '', ''))
    
    return base_url

def is_url(url):
    url_pattern = re.compile(r'http[s]?://[A-Za-z0-9.-]+')

    return bool(url_pattern.match(url))

def get_all_other_urls(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    
    url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

    all_urls = re.findall(url_pattern, str(soup))
    
    domain_url = [uri for uri in all_urls if str(url) in uri.lower() and 'wp' not in uri.lower()]
    filtered_urls = [uri for uri in domain_url if not re.search(r'\.\w+$', uri)]

    final_url = list(set(filtered_urls))

    return final_url

def get_form(url):
    res = requests.get(url)
    main_url = get_base_url(url)
    
    if(res.status_code == 200):
        soup = BeautifulSoup(res.text, "html.parser")

        forms = soup.find_all('form')
        lists = []

        for form in forms:
            input_fields = form.find('input')
            
            param = input_fields['name']
            method = form['method']
            action = form['action']

            if(is_url(action) == False):
                full_url = f'{main_url+action}?{param}='
            else:
                full_url = f'{action}?{param}='
            
            lists.append(full_url)
        
        return lists

    else:
        print(f"Can't reach the {url} page due to {res.status_code} status code")

def post_form(url):
    res = requests.get(url)
    
    if(res.status_code == 200):
        soup = BeautifulSoup(res.text, "html.parser")

        forms = soup.find_all('form')
        form_data_list = []

        for form in forms:
            inputs = form.find_all(['input', 'textarea'])
            form_data = {input_field.get('name'): '' for input_field in inputs if input_field.get('name')}
            form_action = form.get('action')

            form_info = {'data': form_data, 'action': form_action}
            form_data_list.append(form_info)
    
        
        return form_data_list

    else:
        print(f"Can't reach the {url} page due to {res.status_code} status code")

def post_type(form, main_url):
    inputs = form.find_all(['input', 'textarea'])
    form_data = {input_field.get('name'): "fuzzing" for input_field in inputs if input_field.get('name')}

    form_action = form.get('action')
    
    if(is_url(form_action) == False):
        form_info = {'method': 'POST', 'data': form_data, 'action': main_url+form_action}
    else:
        form_info = {'method': 'POST', 'data': form_data, 'action': form_action}
    
    return form_info

def get_type(form, main_url):
    lists = []
    input_fields = form.find_all('input')
    
    if(len(input_fields) > 1):
        for i in range(len(input_fields)):
            try:
                param = input_fields[i]['name']
            except:
                pass
    
            action = form['action']
            
            if(is_url(action) == False):
                full_url = f'{main_url+action}/?{param}='
                form_info = {'method': 'GET', 'data': full_url, 'action': main_url+action}
            else:
                full_url = f'{action}?{param}='
                form_info = {'method': 'GET', 'data': full_url, 'action': action}
                
            lists.append(form_info)
    
    else:
        input_fields = input_fields[0]
        param = input_fields['name']
        method = form['method']
        action = form['action']

        if(is_url(action) == False):
            full_url = f'{main_url+action}?{param}='
            form_info = {'method': 'GET', 'data': full_url, 'action': main_url+action}
        else:
            full_url = f'{action}?{param}='
            form_info = {'method': 'GET', 'data': full_url, 'action': action}
        
        lists.append(form_info)
        
    return lists

def flatten_array(original_array):
    flattened_array = []

    def flatten(array):
        for item in array:
            if isinstance(item, list):
                flatten(item)
            else:
                flattened_array.append(item)

    flatten(original_array)
    return flattened_array

def save_url(result, filename):
    flatten = flatten_array(result)
    
    with open(f'{filename}', 'w') as f:
        for url in flatten:
            try:
                f.write(json.dumps(url))
                f.write('\n')
            except:
                f.write(url + '\n')
    
    with open(filename, 'r') as file:
        lines = file.readlines()

    unique_lines = set(lines)

    with open(filename, 'w') as file:
        file.writelines(unique_lines)

def save_report(url, type, filename, results):
        with open(filename, 'w') as f:
            f.write("Laporan Pengujian SQL Injection")
            f.write("\n\n")
            f.write("URL:\n")
            f.write(url)
            f.write("\n\n")
            f.write("Jenis Pengujian:\n")
            f.write(type)
            f.write("\n\n")
            f.write("Hasil Pengujian:\n")

            if(len(results) > 0):
                for result in results:
                    f.write(result)
                    f.write('\n')
            else:
                f.write(f"[-] Tidak ditemukan kerentanan SQL Injection pada url \"{url}\"\n")
            
            f.write("\n")
            f.write("Hasil Akhir:\n")
            
            if(len(results) > 0):
                f.write(f"Terdapat {len(results)} kemungkinan SQL Injection pada url \"{url}\"")
            else:
                f.write(f"Tidak terdapat kemungkinan SQL Injection pada url \"{url}\"")
        
        print(f"\nHasil pengujian disimpan pada file {filename}\n\n")

     
    

