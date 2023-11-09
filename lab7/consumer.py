import pika
import threading
from datetime import datetime   
from producer import get_parsed_page
import re
from tinydb import TinyDB


def getJson(link):
    soup = get_parsed_page(link)
    
    try:
        register_date = soup.find('span', class_='adPage__aside__stats__owner__registreDate').text.strip()
        last_changes = soup.find('div', class_='adPage__aside__stats__date').text.strip()[20:]
        type_ = soup.find('div', class_='adPage__aside__stats__type').text.strip()[7:]
        views = soup.find('div', class_='adPage__aside__stats__views').text.strip().replace(" ", "")
        all_views, today_views = re.findall(r'\d+', views)
    except Exception as e:
        return {"link":link, "error":str(e)}

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
        "register_date":register_date,
        "last_changes":last_changes,
        "phonenumber":tel,
        "type":type_,
        "overall":all_views,
        "today":today_views,
        "value":price,
        "currency":currency
    }

db = TinyDB('db.json')
db_lock = threading.Lock()

def consumer_thread(thread_id):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    queue_name = 'product_urls'
    channel.queue_declare(queue=queue_name, durable=True)
    print(f'Thread {thread_id}: Waiting for messages.')

    def callback(ch, method, properties, body):
        print(f'Thread {thread_id}: Received {body.decode()}')
        with db_lock:
            db.insert(getJson(body.decode()))
        print(f'Thread {thread_id}: Done')
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=callback)

    channel.start_consuming()

num_threads = 40
threads = []

for thread_id in range(num_threads):
    thread = threading.Thread(target=consumer_thread, args=(thread_id,))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

db.close()