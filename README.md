# luigi-oda-spider

Sample Crawler/Scraper for case study.
It uses [Luigi](https://luigi.readthedocs.io/en/stable/) framework to create a pipeline. 

## How to run
Python (using 3.10 but should work fine on later versions)
- Create a virtual env
  ```sh
  python3.10 -m venv env
  source env/bin/activate
  pip install -e .
  ```
- Run the example command from shell
  ```sh
  bash run.sh
  ```

OR run using
2. Docker
- Build: `docker build -t luigi-oda-crawler:0.0.1 . `
- Run: `docker run --rm -it -v data:/data -e DATA_DIR=/data luigi-oda-crawler:0.0.1`


In both cases, the a current dir. named data will be populated with scraped data as the following structure: `data/<target-name>/<categories>/<prices.csv>`
In the example case, it should be something like: `data/oda/1283-meieri-ost-og-egg/142-ost.csv`

TODO or Improvements:
- Create a local dir (even cloud filesystem) that should be watched by Luigi schudeler for incoming requests for scraping
- Scraping info. should be given using .yaml config files 
- Modify the pipeline to run continously in a deployed state
