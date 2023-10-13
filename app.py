import settings
from settings import Config
import langchain.embeddings
import openai
from urllib.parse import urljoin, urlparse
import utils
import requests
import os
from bs4 import BeautifulSoup
import vectorstore


class Scraper:
    embeddings: langchain.embeddings = None
    config: settings.Config

    dict_done_urls: set
    fileErrors = None
    fileParsed = None

    total_urls_scraped = 0

    _logger = None

    FILE_ERRORS = './errors.txt'
    FILE_SCRAPED = './urls_scraped.txt'

    DIR_SCRAPED = ''
    DIR_CHROMA = ''

    def __new__(cls,  config_file_path='./config.yaml'):
        return super().__new__(cls)
        
    def __init__(self,  config_file_path='./config.yaml'):

        # Laod the configuration to be available to the whole system
        self.config = Config(config_file_path)

        # Set config variables
        self.DIR_SCRAPED = self.config.data['site']['scraped-path']
        self.DIR_CHROMA = self.config.data['vectordb']['chroma-path']

        if Scraper._logger == None:
            Scraper._logger = self.config.getLogger()

        # set the api key for open ai
        openai.api_key = self.config.get_open_ai_key()
        self._logger.debug("Open API key set")

        self._logger.debug("Remove url files from previous runs")
        if os.path.exists(self.FILE_ERRORS):
            # If it exists, delete it
            os.remove(self.FILE_ERRORS)

        if os.path.exists(self.FILE_SCRAPED):
            os.remove(self.FILE_SCRAPED)

        # initialize other objects
        self.dict_done_urls = set()


    def get_config(self):
        return self.config

    def fetch_pdf(self, url: str, destination: str) -> None:
        """ Get a PDF from a URL and persist it as a file

        :param url:
        :param destination:
        :return:
        """
        self._logger.debug("Fetch PDF: " + url)
        try:
            response = requests.get(url)
            with open(destination, 'wb') as output_file:
                output_file.write(response.content)
        except Exception as ex:
            print('Could not write the following PDF: ' + url)
            print(ex)

    def extract_text(self, soup):
        # Removing script and style elements
        for script_or_style in soup(['script', 'style']):
            script_or_style.extract()
        # Getting text
        text = soup.get_text()
        # Removing whitespace
        text = '\n'.join(line.strip() for line in text.strip().splitlines() if line.strip())
        return text

    def scrape_site(self, domain)-> None:

        # Get the list of URL from website
        urlsToScrape = utils.get_urls_from_sitemap(domain)

        # Get urls as a list
        keys = urlsToScrape.keys()

        self.fileErrors = open(self.FILE_ERRORS, 'a')
        self.fileParsed = open(self.FILE_SCRAPED, 'a')

        for i in keys:
            self._logger.debug(f'========= total scraped {self.total_urls_scraped}')

            try:
                self.scrape(i)
            except Exception as e:
                self._logger.debug('eeeeeeeeeeeeeeeeeeeeeee Could not scrape' + str(i))
                self._logger.debug(e)
                self.fileErrors.writelines([i])

        self._logger.debug('done ' + str(self.total_urls_scraped))

        for url in self.dict_done_urls:
            self.fileParsed.write(url + "\n")

        self.fileErrors.close()
        self.fileParsed.close()


    def scrape(self, url, visited=None) -> None:
        """
        Scrapes the given URL, and it crawls the URL via the links within the page
        :param url: the URL to scrape
        :param visited: this allows us to recursively crawl
        :return:
        """
        if visited is None:
            visited = set()  # Set to keep track of visited URLs

        if url in self.dict_done_urls:
            return

        self._logger.debug(f'About to scrape: {url} Number: {len(self.dict_done_urls)}')
        usevecrtordb = self.config.data['site']['use-vector-db']

        # Parse the original URL to get the domain
        original_domain = urlparse(url).netloc

        self._logger.debug(f'Scraping {url}')
        transformed_url = utils.transform_url(url)

        self._logger.debug(f'Transformed {transformed_url}')
        visited.add(url)  # Mark the URL as visited
        self.dict_done_urls.add(url)

        filename, filename_without_extension, file_extension = utils.get_filename_and_extension(url)

        if (file_extension == '.jpg') or (file_extension == '.jpeg') or (
                file_extension == '.png') or (
                file_extension == '.zip') or (
                file_extension == '.mp3'):
            self._logger.debug(f'Skipping file: {filename}')
            return

        if file_extension == '.pdf':
            dir_filename = self.DIR_SCRAPED + filename
            self.fetch_pdf(url, dir_filename )
            if usevecrtordb:
                vectorstore.VectorDB().split_embed_store(dir_filename, '.pdf')
            return

        # Fetch the page
        try:
            response = requests.get(url, timeout=10)
        except requests.exceptions.RequestException as e:
            self._logger.error(f"Failed to retrieve {url}: {e}")
            self.fileErrors.write(str(url + '/n'))
            return

        # If fetch was successful, parse the page with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract all the text for current URL
        url_text = self.extract_text(soup)

        # writeScrapedContent
        utils.write_text_to_file(self.DIR_SCRAPED + transformed_url + '.txt', url_text)

        if usevecrtordb:
            vectorstore.VectorDB().split_embed_store(self.DIR_SCRAPED + transformed_url + '.txt', '.txt')

        # Extract all links
        for a_tag in soup.find_all('a', href=True):
            link = a_tag['href']

            # Resolve relative links to absolute
            link = urljoin(url, link)

            # Normalize the new URL
            link = utils.normalize_url(link)

            # Parse the new URL to get its domain
            link_domain = urlparse(link).netloc

            # Skip already visited links, and limit to same domain
            if link not in visited and link_domain == original_domain:
                self.scrape(link, visited)  # Recursively scrape each link

"""
MAIN
This is the entry point for the scraper
"""
if __name__ == '__main__':

    scraper = Scraper('./config_cdc.yaml')
    scraper.scrape_site(scraper.get_config().get_root_url_to_scrape())


    #scraper.scrape('https://www.orlando.gov/files/sharedassets/public/v/3/departments/oca/22_oca_mmg-applicationguidelines-schoolsandnpo-june2022.pdf')
    #scraper.scrape('https://www.orlando.gov/files/sharedassets/public/departments/edv/main-streets/sodo2.jpeg')








