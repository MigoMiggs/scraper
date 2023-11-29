
H1 Scraper
This project allows the user to scrape a website based on a root domain and 
using the site's sitemap.xml to go as deep as possible. If the sitemap has 
multiple sitemaps, it will try to fetch them all. 

# Setup 

1. Install dependencies <br>
`pip install -r requirements.txt`

2. Make sure that there is a configuration yaml that contains proper settings and Open AI Key. Here is an example config.yaml:
```
embeddings:
  type: "OPEN_AI"

site:
  url: "https://www.orlando.gov"
  name: "city_orlando"
  scraped-path: "./scraped/"
  use-vector-db: True

vectordb:
  chroma-path: "./chroma"
```
Note: You can find existing configuration files under ./config. 

3. Make sure logging levels are adequate within ./config/logging.yaml

4. Make sure you run this in the python console

```
import nltk
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('punkt')
```
5. Create an .env file <br>
Create .env file, with the following:

```
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=
LANGCHAIN_PROJECT=
OPENAI_API_AZURE_BASE=
OPENAI_API_AZURE_KEY=
OPENAI_API_AZURE_ENGINE=
OPENAI_API_AZURE_VERSION=
OPENAI_API_KEY=
```

Running the Scraper
---------------------
1. Run the scraper 
`Usage: app.py <config_file>`

Web Application
---------------
This project also contains a web application that allows the user to submit a question
to get an answer as well as a question with a list of possible answers. Then the 
server will respond back with a chosen answer.

Here are the two different parts of the web application:

### Server
[Server - Readme](./server/README.md)
### Frontend
[Frontend - Readme](./ibts-frontend/README.md)






   
