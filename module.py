import requests
import json 
import time
from typing import List
from colorama import init, Fore, Back, Style
from tqdm import tqdm 
int()
def wayback_urls(domain: str) -> List[str]:
    urls = []
    try: 
        api_url = f"https://web.archive.org/cdx/search/cdx?url={domain}/*&output=json&collapse=urlkey"
        response = requests.get(api_url, timeout=120)
        response.raise_for_status()
        data = response.json()
        for row in data[1:]:
            if len(row) >= 3:
                urls.append(row[2])
        return list(set(urls))
    except requests.RequestException as e:
        print(Fore.RED + "Api error Waybackurls !:" + Style.RESET_ALL, e)
        return []

def urlscan(domain: str, api_key: str = "") -> List[str]:
    urls = []
    try:
        api_url = f"https://urlscan.io/api/v1/search/?q=domain:{domain}"
        headers = {}
        if api_key:
            headers["API-Key"] = api_key
            
        response = requests.get(api_url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        for result in data.get("results", []):
            if "page" in result and "url" in result["page"]:
                urls.append(result["page"]["url"])
        return list(set(urls))
    except requests.RequestException as e:
        print(Fore.RED + "Api error Urlscan.io !: " + Style.RESET_ALL, e)
        return []

def commoncrawl(domain: str) -> List[str]:
    urls = []
    try:
        api_url = "https://index.commoncrawl.org/CC-MAIN-2023-50-index"
        params = {"url": f"*.{domain}/*", "output": "json"}
        response = requests.get(api_url, params=params, timeout=30)
        response.raise_for_status()
    
        for line in response.text.split('\n'):
            if line.strip():
                data = json.loads(line) 
                if "url" in data:
                    urls.append(data["url"])
        return list(set(urls))
    except requests.RequestException as e: 
        print(Fore.RED + "Error Api Commoncrawl !:" + Style.RESET_ALL, e)
        return []

def otx(domain: str, api_key: str) -> List[str]:
    urls = []
    try:
        api_url = f"https://otx.alienvault.com/api/v1/indicators/domain/{domain}/url_list"
        headers = {"X-OTX-API-KEY": api_key} 
        response = requests.get(api_url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        for url_data in data.get("url_list", []):
            if "url" in url_data:
                urls.append(url_data["url"])
        return list(set(urls))
    except requests.RequestException as e:
        print(Fore.RED +"Error api Alienvault ! " + Style.RESET_ALL, e)
        return []

from tqdm import tqdm
import concurrent.futures
import requests

def get_live_urls_fast(urls_list: List[str], max_workers: int = 10) -> List[str]:
    live_urls = []
    
    def check_url_live(url: str) -> tuple:
        try:
            response = requests.head(url, timeout=5, allow_redirects=True)
            return (url, response.status_code == 200)
        except:
            return (url, False)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(check_url_live, url): url for url in urls_list}
        
        for future in tqdm(concurrent.futures.as_completed(future_to_url),
                           total=len(future_to_url),
                           desc="Checking live URLs",
                           colour="green"):
            url, is_live = future.result()
            if is_live:
                live_urls.append(url)
    
    return live_urls
