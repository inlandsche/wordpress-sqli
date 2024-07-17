from scrape_util import *

def do_request(url):
    res = requests.get(url)
    base_url = get_base_url(url)

    result = []

    if (res.status_code == 200):
        soup = BeautifulSoup(res.text, "html.parser")
        forms = soup.find_all('form')

        for form in forms:
            try:
                method = (form['method']).lower()

                if (method == "post"):
                    res = post_type(form, base_url)
                    result.append(res)
                elif (method == "get"):
                    result.append(get_type(form, base_url))
                else:
                    print("Method not yet supported!")
            except Exception as e:
                pass
                
        return result

    else:
        print(f"Can't reach the {url} page due to {res.status_code} status code")