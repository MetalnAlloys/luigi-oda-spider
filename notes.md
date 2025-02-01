## Case study
### Tasks
- fetch entire product catalogue
- metadaata e.g. prices
- Product Availability

Output:
- CSV or json -> Pandas dataframes?

Important:
- Peformance. Concurrency?
- Reusability. Modular, Abstracted 
- Avoid Throttling or load balancer limits
- Separate config.
- Visualization . Pandoc, Pandas?


## Oda Policy
https://oda.com/robots.txt
https://oda.com/sitemap.xml



## Notes
- Crawling: iterate through data
- Scraping: Turning unstructured data into structured data
- Scraper is a subset of a crawler

### Design (Crawler)

Start URL -> (Control loop) -> [Spider (Scraper->processors)]

Items needed:
1. Root URL of the target
2. Spider (Concurrent Design): 
- Scraper: Fetch URLs, parse data, transform data, list of URLs
- Processor: Process the data e.g. for the DB



## Implementation
Libraries: 
- Stdlib
- Requests
- Luigi, for creating a pipeline
- Beautiful Soup, parse HTML 

First try Static only
