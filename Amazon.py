import requests #pip install requests
from bs4 import BeautifulSoup #pip install bs4
import os
import time
import json
import random
import schedule
from Database import Data
from Update import send_message

# Google "My User Agent" And Replace It

headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'} 

#Checking the price
def check_single_price(ASIN):
    URL = "https://www.amazon.de/dp/" + ASIN + "/"
    page = requests.get(URL, headers=headers)
    soup  = BeautifulSoup(page.content, 'html.parser')

    #Finding the elements
    product_title = soup.find(id='productTitle').text

    if soup.find(id='corePrice_desktop') is not None:
        try:
            product_price = soup.find(id='corePrice_desktop')
            product_price = product_price.findAll("span", {"class", "a-price a-text-price a-size-medium apexPriceToPay"})[0]
            product_price = product_price.findAll("span", {"class", "a-offscreen"})[0].text
        except IndexError:
            pass
    elif len(soup.findAll("span", {"class":"a-price-whole"})) != 0:
        try:
            product_price = soup.findAll("span", {"class":"a-price-whole"})[0].text
            product_price = product_price + soup.findAll("span", {"class":"a-price-fraction"})[0].text + "€"
        except IndexError:
            pass
    else:
        print("Couldn't get price at " + ASIN)
        product_price = -1
    dic = {"asin":ASIN, "title":product_title.replace("  ", ""), "price":product_price}
    return dic

def check_search(TERM):
    TERM = TERM.replace(" ", "+")
    URL = "https://www.amazon.de/s?k=" + TERM

    page = requests.get(URL, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')

    product_list = soup.findAll("div", {"class":"s-main-slot s-result-list s-search-results sg-row"})[0]
    product_list = product_list.findAll("div", {"class":"s-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 sg-col s-widget-spacing-small sg-col-12-of-16"})

    products = []

    for product in product_list:
        asin = product["data-asin"]
        title = product.findAll("h2", {"class":"a-size-mini a-spacing-none a-color-base s-line-clamp-2"})[0].text
        try:
            price = str(product.findAll("span", {"class":"a-price-whole"})[0].text) + "€"
        except IndexError:
            price = -1
        dic = {"asin":asin, "title": title, "price": price}
        products.append(dic)
    return products

def amazon_thread(data, check_time):
    minute = random.randint(0,60)
    check_time = str(check_time) + ":" + str(minute)
    schedule.every().day.at(check_time).do(start,data)

def start(api_key, chat_ids):

    data = Data()
    
    print("Start searching")
    # search_term = data.get_amazon_search_terms()
    search_terms = ["Galaxy A","8 GB RAM"]
    asins = []
    for term in search_terms:
        time.sleep(random.uniform(0,30))
        timestamp = time.time()
        products = check_search(term)
        for product in products:
            asins.append(product["asin"])
            if not data.product_exists(product["asin"]):
                data.add_amazon_product(product["title"], product["asin"])
            data.add_amazon_search_instance(term, timestamp)
            data.add_amazon_search_result(term, timestamp, product["asin"])
            data.add_amazon_price(product["asin"], product["price"], timestamp)
            if(data.check_drop(product["asin"], 0.1)):
                for chat in chat_ids:
                    send_message("Das Produkt \n\n" + product["title"] + "\nmit dem Link: https://www.amazon.de/dp/" + product["asin"] + "/\n\nist signifikant im Preis gefallen"
                                + "\n\n das Produkt wurde im Rahmen des Surch-Terms '" + term + "' aufgezeichnet")

    # watchlist = data.get_watchlist()
    watchlist = [["B08ZLW675G"],["B07CMH5F9R"],["B081QX9V2Y"],["B08CVJ59G3"], ["B09L61QRM1"]]

    watchlist = [e for e in watchlist if e[0] not in asins]
    print(watchlist)
    for element in watchlist:
        timetamp = time.time()
        result = check_single_price(element[0])
        data.add_amazon_price(result["asin"], result["price"], timetamp)
        if(data.check_drop(result["asin"], 0.1)):
            for chat in chat_ids:
                send_message("Das Produkt \n\n" + result["title"] + "\nmit dem Link: https://www.amazon.de/dp/" + result["asin"] + "/\n\nist signifikant im Preis gefallen", chat, api_key)
        time.sleep(random.uniform(0,30))




api = "1719127362:AAHSCLN1M5BoGg3pt3AUYz0MH7W8uPvIcfY"
chat_ids = ["653734838"]

# start(data, api, chat_ids)

# check_search("Galaxy A")