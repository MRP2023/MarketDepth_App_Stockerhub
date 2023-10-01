import requests
from bs4 import BeautifulSoup
import datetime
import os
import pickle
from cache import Cache
import redis

# Create a cache instance
# cache = Cache()
# cache = {}



redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)



# Define a function to fetch data from the web or cache
def fetch_or_cache_data(instr_code):
    # cached_data = cache.get(instr_code)
    cached_data = redis_client.get(instr_code)

    if cached_data is not None:
        # If data is in the cache, return it
        print(f"Using cached data for {instr_code}")
        return pickle.loads(cached_data)


    
    # if cached_data is not None:
    #     # If data is in the cache, return it
    #     print(f"Using cached data for {instr_code}")
    #     return cached_data



    # if instr_code in cache:
    #     # If data is in the cache, return it
    #     print(f"Using cached data for {instr_code}")
    #     return cache[instr_code]

    # Fetch data from the web
    print(f"Fetching data from the web for {instr_code}")
    if instr_code == "KAY":
        instr_code = "KAY%26QUE"
    if instr_code == "AMCL":
        instr_code = "AMCL%28PRAN%29"
    
    company_name = instr_code.replace("&", "%26")
    api_url = "https://dsebd.org/ajax/load-instrument.php"

    s = requests.Session()

    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br, json',
        'accept-language': 'en-US,en;q=0.9',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://dsebd.org',
        'Referer': 'https://dsebd.org/mkt_depth_3.php',
        'sec-ch-ua': '"Chromium";v="107", "Not A(Brand";v="21", "Google Chrome";v="107"',
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Length': "0",
    }

    r = s.post(api_url, data="inst=" + company_name, headers=headers)
    tables = BeautifulSoup(r.text, "html.parser").findAll("table")

    output = {"buyers": [], "sellers": []}

    if len(tables) >= 4:
        buy_data = tables[2].findAll("td")
        sell_data = tables[3].findAll("td")

        if len(buy_data) > 2:
            i = 3
            while i + 1 <= len(buy_data):
                buyer = dict()
                buyer["Instr_Code"] = company_name
                buyer["buyer_price"] = float(buy_data[i].text.replace(",", ""))
                buyer["buyer_volume"] = float(buy_data[i + 1].text.replace(",", ""))
                buyer["date"] = str(datetime.datetime.utcnow().strftime("%Y-%m-%d"))
                output["buyers"].append(buyer)
                i += 2

        if len(sell_data) > 2:
            i = 3
            while i + 1 <= len(sell_data):
                seller = dict()
                seller["Instr_Code"] = company_name
                seller["seller_price"] = float(sell_data[i].text.replace(",", ""))
                seller["seller_volume"] = float(sell_data[i + 1].text.replace(",", ""))
                seller["date"] = str(datetime.datetime.utcnow().strftime("%Y-%m-%d"))
                output["sellers"].append(seller)
                i += 2
    
    # ... Rest of your fetching code ...

    # Cache the fetched data
    # cache[instr_code] = output
    # cache.add(instr_code, output)
    redis_client.set(instr_code, pickle.dumps(output))


    return output

# Rest of your code remains the same
def get_market_depth_of_a_company(instr_code):
    # Call the fetch_or_cache_data function to fetch or use cached data
    return fetch_or_cache_data(instr_code)






# Read instrument codes from a text file
txt_filepath = os.path.join("/home/pantho/Desktop", "instrument_codes.txt")
with open(txt_filepath, "r") as txt_file:
    for line in txt_file:
        instr_code = line.strip()
        print(f"Getting market depth for {instr_code}")
        result = get_market_depth_of_a_company(instr_code)
        # Process the result as needed
        print(result)