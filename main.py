"""
main.py

This file scrapes a given website, creates embeddings and sticks them into an
instance of chroma DB (vector DB) which generates embeddings for the site
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
import openai
import os
import utils

SITEMAP_URI = '/sitemap.xml'
BEGIN_URL = 'https://www.orlando.gov'

FILE_ERRORS = './errors.txt'
FILE_SCRAPED = './urls_scraped.txt'

DIR_SCRAPED = './scraped/'
DIR_CHROMA = './chroma'

TOTAL_SCRAPED = 0
dictDoneUrls = set()
erroredURLs = set()

embedding = OpenAIEmbeddings()
persist_directory = './chroma/'

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,
    chunk_overlap=150
)

vectordb = None


def fetch_pdf(url: str, destination: str) -> None:
    """ Get a PDF from a URL and persist it as a file

    :param url:
    :param destination:
    :return:
    """
    try:
        response = requests.get(url)
        with open(destination, 'wb') as output_file:
            output_file.write(response.content)
    except Exception as ex:
        print('Could not write the following PDF: ' + url)
        print(ex)


def write_text_to_file(filename: str, text: str) -> None:
    """
    Writes file to disk
    :param filename:
    :param text:
    :return:
    """
    global TOTAL_SCRAPED
    TOTAL_SCRAPED = TOTAL_SCRAPED + 1

    print(f'total scraped {TOTAL_SCRAPED}')

    # Check if the file exists
    if os.path.exists(filename):
        # If it exists, go back
        return

    # Whether the file existed or not, create a new file and write the text into it
    with open(filename, 'w') as file:
        file.write(text)
        file.close()


def split_embed_store(filename: str, ext: str) -> None:
    global vectordb

    loader = None
    if ext == '.pdf':
        # loaders.append(PyPDFLoader('./scraped/' + f))
        print(filename)
    else:
        loader = TextLoader(filename)

    if loader is not None:
        docs = loader.load_and_split(text_splitter)

        if vectordb is None:
            vectordb = Chroma.from_documents(
                documents=docs,
                embedding=embedding,
                persist_directory=persist_directory
            )
        else:
            vectordb.add_documents(documents=docs)


def transform_url(url: str) -> str:
    # Strip out the 'http://' or 'https://' part
    parsed_url = urlparse(url)
    stripped_url = parsed_url.netloc + parsed_url.path

    # Replace dots with underscores
    url_with_underscores = stripped_url.replace('.', '_')

    # Replace slashes with dashes
    transformed_url = url_with_underscores.replace('/', '-')

    return transformed_url


def normalize_url(url):
    parsed_url = urlparse(url)
    # Reconstruct the URL without the query and fragment components
    normalized_url = urlunparse(
        (parsed_url.scheme, parsed_url.netloc, parsed_url.path, None, None, None)
    )
    return normalized_url


def extract_text(soup):
    # Removing script and style elements
    for script_or_style in soup(['script', 'style']):
        script_or_style.extract()
    # Getting text
    text = soup.get_text()
    # Removing whitespace
    text = '\n'.join(line.strip() for line in text.strip().splitlines() if line.strip())
    return text


def get_urls_from_sitemap(url: str) -> dict:
    url_sitemap = url + SITEMAP_URI

    response = requests.get(url_sitemap)
    if response.status_code == 200:
        parcala = BeautifulSoup(response.content, "xml")
    else:
        print(f'Failed to retrieve sitemap: {response.status_code}')
        exit()

    urls_from_xml = {}
    loc_tags = parcala.find_all('loc')

    for loc in loc_tags:
        urls_from_xml[loc.text] = ''

    urls_from_xml[url] = ''

    print(f'Number of URLs to walk: ' + str(len(urls_from_xml)))
    return urls_from_xml


def scrape(url, visited=None) -> None:
    """
    Scrapes the given URL, and it crawls the URL via the links within the page
    :param url: the URL to scrape
    :param visited: this allows us to recursively crawl
    :return:
    """
    if visited is None:
        visited = set()  # Set to keep track of visited URLs

    if url in dictDoneUrls:
        return

    # Parse the original URL to get the domain
    original_domain = urlparse(url).netloc

    print(f'Scraping {url}')
    transformed_url = transform_url(url)

    print(f'Transformed {transformed_url}')
    visited.add(url)  # Mark the URL as visited
    dictDoneUrls.add(url)

    filename, filename_without_extension, file_extension = utils.get_filename_and_extension(url)

    if file_extension == '.pdf':
        fetch_pdf(url, DIR_SCRAPED + filename)

    if (file_extension == '.jpg') or (file_extension == 'jpeg') or (file_extension == '.png'):
        return

    # Fetch the page
    try:
        response = requests.get(url, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve {url}: {e}")
        fileErrors.writelines(url + '/n')
        return

    # If fetch was successful, parse the page with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract all the text for current URL
    url_text = extract_text(soup)

    # writeScrapedContent
    write_text_to_file(DIR_SCRAPED + transformed_url + '.txt', url_text)
    split_embed_store(DIR_SCRAPED + transformed_url + '.txt', '.txt')

    # Extract all links
    for a_tag in soup.find_all('a', href=True):
        link = a_tag['href']

        # Resolve relative links to absolute
        link = urljoin(url, link)

        # Normalize the new URL
        link = normalize_url(link)

        # Parse the new URL to get its domain
        link_domain = urlparse(link).netloc

        # Skip already visited links, and limit to same domain
        if link not in visited and link_domain == original_domain:
            scrape(link, visited)  # Recursively scrape each link


def initialize() -> None:
    if os.path.exists(FILE_ERRORS):
        # If it exists, delete it
        os.remove(FILE_ERRORS)

    if os.path.exists(FILE_SCRAPED):
        os.remove(FILE_SCRAPED)


"""
MAIN
This is the entry point for the scraper
"""
if __name__ == '__main__':

    openai.api_key = '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'

    # Get the list of URL from website
    urlsToScrape = get_urls_from_sitemap(BEGIN_URL)
    # Get urls as a list
    keys = urlsToScrape.keys()

    fileErrors = open(FILE_ERRORS, 'a')
    fileParsed = open(FILE_SCRAPED, 'a')

    for i in keys:
        print(f'========= total scraped {TOTAL_SCRAPED}')

        try:
            scrape(i)
        except Exception as e:
            print('eeeeeeeeeeeeeeeeeeeeeee Could not scrape' + str(i))
            print(e)
            fileErrors.writelines([i])

    print('done ' + str(TOTAL_SCRAPED))

    for url in dictDoneUrls:
        fileParsed.write(url + "\n")

    fileErrors.close()
    fileParsed.close()
