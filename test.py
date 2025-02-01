import requests
import csv
import re
import os
from bs4 import BeautifulSoup

#url_pattern = "^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"

def calc_price(price_str):
    if price_str:
        return price_str.replace(u'\xa0', ' ').split(' ')[1]
    else:
        return "0.00"


links_visited = []

BASE_URL = "https://oda.com/no"
url_to_start = "/products/"
sub_search_keyword = "categories"

url_start = BASE_URL + url_to_start

response = requests.get(url_start)
soup = BeautifulSoup(response.content, 'html.parser')

urls = set()
for link in soup.find_all('a', attrs={'href': re.compile(r"^https://.*{}.*".format(sub_search_keyword))}):
    urls.add(link.get('href'))

for url in urls:
    if url in links_visited:
        print("[X] Already visited: {}".format(url))
        continue

    print("[+] Scraping: {}".format(url))

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    suffix = url.strip("/").split("/")[-1]

    uri_set = set()
    # exclude http[s]
    #for uri in soup.find_all('a', attrs={'href': re.compile(r"^(?!(https)).*")}):
    for uri in soup.find_all('a', attrs={'href': re.compile(suffix)}):
        href = uri.get("href")
        if href == url or "?filters=" in href or re.search(r"{}/$".format(suffix), href):
            continue
        uri_set.add(uri.get("href"))

    # handle pagination (load more). Unable to figure out how many pages to crwal

    for i in range(1, 10):
        for uri in uri_set:
            Utsolgt = False
            #print("[++] Scraping Page index {}".format(i))
            main_url = "https://oda.com" + uri + f'?cursor={i}'

            print("Crawling: {}".format(main_url))

            response = requests.get(main_url)
                
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = soup.find_all("article")

            for article in articles:
                data = []
                filtered_values = list(filter(lambda v: re.match('^styles', v), article["class"]))
                if len(filtered_values) == 0:
                    continue
                item_name = article.h2.text

                price_str = article.find_all("span")[1].get_text(strip=True)

                price = ""
                if price_str == "Utsolgt":
                    Utsolgt = True
                    price = article.find_all("span")[2].get_text(strip=True)
                else:
                    price = calc_price(price_str)

                # print(f"Extracted price: {price_str}")
                # print(f"Calculated price: {price}")
                # print("Item: {}, price: {}".format(item_name, price))

                floatprice = 0.0
                try:
                    floatprice = float(price.replace(',', '.'))
                except ValueError:
                    floatprice = 0.0

                #print(f"Float: {floatprice}")
                data.append({'item': item_name, 'price': floatprice, 'status': "Utsolgt" if Utsolgt else "Tilgjengelig"})

                data_store = f"data/{suffix}"
                if not os.path.exists(data_store):
                    os.makedirs(data_store)

                filename = main_url.rsplit("/", 1)[0].split("/")[-1] + ".csv"
                full_filepath = f'{data_store}/{filename}'

                with open(full_filepath, 'a', newline='') as csvfile:
                   fieldnames = ['item', 'price', 'status']
                   writer = csv.DictWriter(csvfile, fieldnames=fieldnames, restval=' ')
                   if csvfile.tell() == 0:
                       writer.writeheader()
                   writer.writerows(data)


    links_visited.append(url)

    print("==================")







