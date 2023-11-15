# Scraper
This project allows the user to scrape a web site based on a root domain and 
using the site's sitemap.xml to go as deep as possible. 

# Setup 

1. Install dependencies <br>
`pip install -r requirements.txt`
2. Make sure that there is a configuration yaml that containst proper settings and Open AI Key. Here is an example config.yaml:
```
logging:
  level: "INFO"
  logfile: "./scraperlog"

embeddings:
  type: "OPEN_AI"

site:
  url: "https://www.orlando.gov"
  sitemap: "/sitemap.xml"
  name: "city_orlando"
  scraped-path: "./scraped/"
  use-vector-db: True

openai:
  key: "sk-pppppppp"

vectordb:
  chroma-path: "./chroma"
```
3. Make sure logging levels are adequate within logging.yaml

4. Make sure you run this in the python console

import nltk
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('punkt')


   
