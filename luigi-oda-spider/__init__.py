import datetime
import requests
import csv
import re
import os
from bs4 import BeautifulSoup
import luigi


def strnow():
    return datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S.%f")


def calc_price(price_str):
    if price_str:
        return price_str.replace(u'\xa0', ' ').split(' ')[1]
    else:
    # Avoiding the case for discountef items for now
        return "0.00"


class GetLinks(luigi.Task):
    base_url = luigi.Parameter()

    def output(self):
        return luigi.LocalTarget("data/urls.txt")

    def run(self):
        BASE_URL = "https://oda.com/no"
        url_to_start = "/products/"
        sub_search_keyword = "categories"

        # e.g.  https://oda.com/no/products/categories/

        url_start = BASE_URL + url_to_start
        response = requests.get(url_start)
        soup = BeautifulSoup(response.content, 'html.parser')

        urls = set()
        for link in soup.find_all('a', attrs={'href': re.compile(r"^https://.*{}.*".format(sub_search_keyword))}):
            urls.add(link.get('href'))

        with self.output.open("w") as f:
            for link in urls:
                f.write(link)



class GetProducts(luigi.Task):
    """
    Extract the Oda product catalogue
    """
    def output(self):
        return luigi.LocalTarget("data/books_list.txt")

    def run(self):
        with open()




