import datetime
import requests
import csv
import re
import os
from bs4 import BeautifulSoup
import luigi
import luigi.contrib.opener
from urllib.parse import urlparse
import yaml
import logging
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import urllib.robotparser


DATA_DIR = os.environ.get("DATA_DIR", "/tmp/data")

def strnow():
    return datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S.%f")


def calc_price(price_str):
    if price_str:
        return price_str.replace(u'\xa0', ' ').split(' ')[1]
    else:
    # Avoiding the case for discounted items for now
        return "0.00"



class GetLinksToCrawl(luigi.Task):
    """
    Get links recursively to crawl
    """
    base_url = luigi.Parameter()
    urls_file = luigi.Parameter()


    def output(self):
        return luigi.LocalTarget(self.urls_file)

    def run(self):
        uri_path = "/products"
        uri_subpath = "/categories"
        url_start = str(self.base_url) + uri_path

        # Use exp. backoff
        # backoff_factor * (2 ** (current_number_of_retries - 1))
        try:
            retry = Retry(
                total=5,
                backoff_factor=2,
                status_forcelist=[429, 500, 502, 503, 504],
            )

            adapter = HTTPAdapter(max_retries=retry)
            session = requests.Session()

            session.mount('https://', adapter)
            headers = {'User-Agent': 'Oda test crawler bot. Contact ali.scmenust@gmail.com'}

            r = session.get(url_start, headers=headers, timeout=30)

            soup = BeautifulSoup(r.content, 'html.parser')

            # Avoiding dupicates
            urls = set()

            for link in soup.find_all('a', attrs={'href': re.compile(r"^https://.*{}.*".format(uri_subpath))}):
                urls.add(link.get('href'))

            with self.output().open("w") as f:
                for link in soup.find_all('a', attrs={'href': re.compile(r"^https://.*{}.*".format(uri_subpath))}):
                    urls.add(link.get('href'))
                for url in urls:
                    f.write(url + '\n')

        except Exception as e:
            print(e)



class GetProducts(luigi.Task):
    """
    Extract the Oda product catalogue
    """
    target_name = luigi.Parameter()
    retry_on_error = luigi.Parameter(default=False)
    base_url = luigi.Parameter()
    #uri_path = luigi.Parameter()
    # sub_uri_path = luigi.Parameter(default="categories")

    def datadir(self):
        return luigi.LocalTarget(os.path.join(DATA_DIR, str(self.target_name)))


    def url_config_target(self):
        return luigi.LocalTarget('%s/urls.txt' % (self.datadir().path))


    def requires(self):
        # return luigi.task.externalize(GetLinksToCrawl( urls_file=self.url_config_target().path, base_url = self.base_url))
        return GetLinksToCrawl( urls_file=self.url_config_target().path, base_url = self.base_url)

    
    def run(self):
        links_visited = list()

        logger = logging.getLogger('luigi-interface')
        logger.info("Running --> Agg.Task")

        with open(self.url_config_target().path) as urls:
            for url in urls:
                # Extra measure to not overload the server
                url = url.strip()
                if url in links_visited:
                    print("Already visited: {}".format(url))
                    continue

                print("[+] Scraping: {}".format(url))

                try:
                    retry = Retry(
                        total=2,
                        backoff_factor=2,
                        status_forcelist=[429, 500, 502, 503, 504],
                    )

                    adapter = HTTPAdapter(max_retries=retry)
                    session = requests.Session()

                    session.mount('https://', adapter)
                    headers = {'User-Agent': 'Oda test crawler bot. Contact ali.scmenust@gmail.com'}

                    r = session.get(url, headers=headers, timeout=60)

                    soup = BeautifulSoup(r.content, 'html.parser')
                    suffix = url.strip("/").split("/")[-1] # e.g. 391-salat-og-kal

                    uri_set = set()

                    # Alternatively trying to exclude all https urls e.g. 
                    # for uri in soup.find_all('a', attrs={'href': re.compile(r"^(?!(https)).*")}):
                    for uri in soup.find_all('a', attrs={'href': re.compile(suffix)}):
                        href = uri.get("href")
                        if href == url or "?filters=" in href or re.search(r"{}/$".format(suffix), href):
                            continue
                        uri_set.add(uri.get("href"))


                    # handle pagination (load more button).
                    # Note: Unable to figure out how many pages to crawl, so
                    # setting the limit to 
                    for i in range(1, 5):
                        for uri in uri_set:
                            # Flag the item as "Utsolgt for later use" 
                            Utsolgt = False

                            main_url = "https://oda.com" + uri + f'?cursor={i}'
                            print("[+] Crawling: {}".format(main_url))

                            response = session.get(main_url)
                                
                            soup = BeautifulSoup(response.content, 'html.parser')

                            # Using the <article> tag in HTML source code. I am
                            # sure there are better ways
                            articles = soup.find_all("article")

                            for article in articles:
                                data = []
                                # Use this to avoid parsing <articles> that do not have product info e.g. warnings and notification
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

                                data_store = os.path.join(self.datadir().path, suffix)
                                if not os.path.exists(data_store):
                                    os.makedirs(data_store)

                                # e.g. data/oda/391-salat-og-kal/
                                filename = main_url.rsplit("/", 1)[0].split("/")[-1] + ".csv"
                                full_filepath = os.path.join(self.datadir().path, suffix, filename)


                                with open(full_filepath, 'a+', newline='') as csvfile:
                                   fieldnames = ['item', 'price', 'status']
                                   writer = csv.DictWriter(csvfile, fieldnames=fieldnames, restval=' ')
                                   if csvfile.tell() == 0:
                                       writer.writeheader()
                                   writer.writerows(data)


                except Exception as e:
                    print(e)


                links_visited.append(url)

        with self.output().open("w") as f:
            f.write("DONE")

                

    def output(self):
         return luigi.LocalTarget('%s/DONE' % (self.datadir().path))









