import requests
from bs4 import BeautifulSoup
import re

def get_parsed_page(URL:str):
    resp = requests.get(URL)
    soup = BeautifulSoup(resp.text, 'html.parser')
    return soup
 
def get_all_link_products(soup) -> set:
    links = soup.find_all('a')
    products_not_filtered = []
    for link in links:
        href = link.get('href')
        if href:
            clas = link.get("class")
            if clas is not None:
                if "js-item-ad" in clas:
                    products_not_filtered.append(href.strip())

    products = set()
    for product in products_not_filtered:
        if re.search("/ro/[0-9]+", product) is not None:
            products.add("https://999.md" + product)

    return products

def getMaxPage(soup):
    lis = soup.find_all('li')
    for li in lis:
        clas = li.get('class')
        if clas is not None:
            if clas == ["is-last-page"]:
                return li.find('a').get("href")

def find_all_pages(URL, max_pages, last_page):
    out = []
    i = 1
    request_url = ""
    while i <= max_pages:
        if i == 1:
            request_url = URL
        else:
            request_url = f"{URL}?page={i}"

        all_products = get_all_link_products(get_parsed_page(request_url))
        out.append(all_products)
        
        if request_url == last_page:
            break
        i += 1

    return out

def find_all_pages_recursive(base_url, request_url, i, max_pages, last_page, out=[]):
    if i > max_pages:
        return

    soup = get_parsed_page(request_url)
    out.append(get_all_link_products(soup))

    if last_page == request_url:
        return

    find_all_pages_recursive(base_url, f"{base_url}?page={i + 1}", i + 1, max_pages, last_page, out)
    
if __name__ == "__main__":
    URL = "https://999.md/ro/list/transport/cars"
    # find_all_pages(URL, 2, "https://999.md" + getMaxPage(get_parsed_page(URL)))
    # out = []
    # find_all_pages_recursive(URL, URL, 1, 10, "https://999.md" + getMaxPage(get_parsed_page(URL)), out)

    


    
    