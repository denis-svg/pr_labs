from datetime import datetime   
from in_class import get_parsed_page

def getJson(link):
    soup = get_parsed_page(link)
    
    register_date = soup.find('span', class_='adPage__aside__stats__owner__registreDate').text.strip()
    last_changes = soup.find('div', class_='adPage__aside__stats__date').text.strip()[20:]
    type_ = soup.find('div', class_='adPage__aside__stats__type').text.strip()[7:]
    views = soup.find('div', class_='adPage__aside__stats__views').text.strip().replace(" ", "")
    all_views, today_views = re.findall(r'\d+', views)

    price = soup.find('span', class_='adPage__content__price-feature__prices__price__value')
    if price:
        price = price.text.strip().replace(" ", "")
    currency = soup.find('span', class_='adPage__content__price-feature__prices__price__currency')
    if currency:
        currency = currency.text.strip()

    
    owner = ""
    tel = ""
    a_tags = soup.find_all('a')
    for a in a_tags:
        href = a.get("href")
        if href is not None:
            if re.search("/ro/profile/", href):
                owner = "https://999.md" + href
                break

    for a in a_tags:
        href = a.get("href")
        if href is not None:
            if re.search("tel", href):
                tel = href[4:]
                break

    return {
        "link":link,
        "owner":owner,
        "date":{
            "register_date":register_date,
            "last_changes":last_changes
        },
        "phonenumber":tel,
        "type":type_,
        "views":{
            "overall":all_views,
            "today":today_views
        },
        "price":{
            "value":price,
            "currency":currency
        },

    }

if __name__ == "__main__":
    print(getJson("https://999.md/ro/60276483"))