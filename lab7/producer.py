import requests
from bs4 import BeautifulSoup
import re
import pika

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

def send_urls(URL, max_pages, last_page):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    queue_name = 'product_urls'
    channel.queue_declare(queue=queue_name, durable=True)
    i = 1
    request_url = ""
    while i <= max_pages:
        if i == 1:
            request_url = URL
        else:
            request_url = f"{URL}?page={i}"

        print(request_url)
        products_urls = get_all_link_products(get_parsed_page(request_url))

        for page_url in products_urls:
            channel.basic_publish(exchange='', routing_key=queue_name, body=page_url)

        
        if request_url == f"{URL}?page={last_page}":
            break
        i += 1

    connection.close()


if __name__ == "__main__":
    URL = "https://999.md/ro/list/transport/cars"
    send_urls(URL, 1, 10)
    
