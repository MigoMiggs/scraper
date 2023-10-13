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

