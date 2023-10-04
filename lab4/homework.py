import requests
from bs4 import BeautifulSoup

def getProducts(URL):
    i = 0
    resp = requests.get(URL)

    while resp.status_code == 200:
        soup = BeautifulSoup(resp.text, 'html.parser')
        divs = soup.find_all('div')

        products = []
        for div in divs:
            h1s = div.find_all("h1")
            json = {
                "name":h1s[0].text,
                "author":h1s[1].text,
                "price":h1s[2].text,
                "description":h1s[3].text,
            }
            products.append(json)
        i += 1
        resp = requests.get(f"{URL} + {i}")
    return products

if __name__ == "__main__":
    URL = "http://127.0.0.1:8080/product/"
    print(getProducts(URL))


