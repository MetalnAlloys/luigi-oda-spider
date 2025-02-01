import datetime
import requests
import csv
import re
import os
from bs4 import BeautifulSoup
import luigi
import luigi.contrib.opener
import luigi.local_target


def strnow():
    return datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S.%f")


def calc_price(price_str):
    if price_str:
        return price_str.replace(u'\xa0', ' ').split(' ')[1]
    else:
    # Avoiding the case for discounted items for now
        return "0.00"


def get_links_to_crawl(base_url):
    url_to_start = "/products/"
    sub_search_keyword = "categories"

    # e.g.  https://oda.com/no/products/
    url_start = base_url + url_to_start

    response = requests.get(url_start)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Avoiding dupicates
    urls = set()

    for link in soup.find_all('a', attrs={'href': re.compile(r"^https://.*{}.*".format(sub_search_keyword))}):
        urls.add(link.get('href'))

    with open("urls.txt", "w") as f:
        for link in urls:
            f.write(link + '\n')



class GetProducts(luigi.Task):
    """
    Extract the Oda product catalogue
    """

    name = luigi.Parameter()

    def output(self):
        return luigi.contrib.opener.OpenerTarget(self.name)

    def run(self):
        links_visited = list()

        with open("urls.txt") as urls:
            for url in urls:
                # Extra measure to not overload the server
                if url in links_visited:
                    print("Already visited: {}".format(url))
                    continue

                print("[+] Scraping: {}".format(url))

                response = requests.get(url)
                soup = BeautifulSoup(response.content, 'html.parser')

                suffix = url.strip("/").split("/")[-1] # e.g. 391-salat-og-kal

                uri_set = set()

                # exclude http[s]
                # for uri in soup.find_all('a', attrs={'href': re.compile(r"^(?!(https)).*")}):

                for uri in soup.find_all('a', attrs={'href': re.compile(suffix)}):
                    href = uri.get("href")
                    if href == url or "?filters=" in href or re.search(r"{}/$".format(suffix), href):
                        continue
                    uri_set.add(uri.get("href"))
                
                # handle pagination (load more button).
                # Note: Unable to figure out how many pages to crawl, so
                # setting the limit to 10
                for i in range(1, 10):
                    for uri in uri_set:
                        # Flag the item as "Utsolgt for later use" 
                        Utsolgt = False

                        main_url = "https://oda.com" + uri + f'?cursor={i}'

                        print("Crawling: {}".format(main_url))

                        response = requests.get(main_url)
                            
                        soup = BeautifulSoup(response.content, 'html.parser')

                        # Using the <article> tag in HTML source code. I am
                        # sure there are better ways

                        articles = soup.find_all("article")

                        for article in articles:
                            data = []

                            # Use this to avoid parsing <articles> that do not
                            # have product info e.g. warnings and notification
                            # messages. Searching for the "styles__" string
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

                            # Convert the Extracted price to float for CSV file
                            # Better done using pandas library. Just a hack right now
                            floatprice = 0.0
                            try:
                                floatprice = float(price.replace(',', '.'))
                            except ValueError:
                                floatprice = 0.00

                            data.append({'item': item_name, 'price': floatprice, 'status': "Utsolgt" if Utsolgt else "Tilgjengelig"})

                            data_store = f"data/{suffix}"
                            if not os.path.exists(data_store):
                                os.makedirs(data_store)

                            filename = main_url.rsplit("/", 1)[0].split("/")[-1] + ".csv"
                            full_filepath = f'{data_store}/{filename}'

                            with open(full_filepath, 'a', newline='') as csvfile:
                               fieldnames = ['item', 'price', 'status']
                               writer = csv.DictWriter(csvfile, fieldnames=fieldnames, restval=' ')

                               # Again, better done using pandas
                               if csvfile.tell() == 0:
                                   writer.writeheader()

                               writer.writerows(data)

                links_visited.append(url)







