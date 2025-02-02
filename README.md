# luigi-oda-spider

Sample Crawler/Scraper for case study.

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


In both cases, the a current dir. named data will be populated with scraped data e.g. `data/<target-name>/<categories>/<prices.csv>`
