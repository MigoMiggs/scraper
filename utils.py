import os
from urllib.parse import urlparse, urlunparse
import app
import logging
import requests
from bs4 import BeautifulSoup

import settings


logger = logging.getLogger(app.Scraper.__name__)

def get_filename_and_extension(url: str):
    parsed_url = urlparse(url)
    path = parsed_url.path
    filename = os.path.basename(path)
    filename_without_extension, file_extension = os.path.splitext(filename)
    return filename, filename_without_extension, file_extension


def write_text_to_file(filename: str, text: str) -> None:
    """
    Writes file to disk
    :param filename:
    :param text:
    :return:
    """
    logger = logging.getLogger('app.Scraper')
    logger.debug("Writing file: " + filename)

    # Check if the file exists
    if os.path.exists(filename):
        # If it exists, go back
        logger.debug("File exists, skip.")
        return

    # Whether the file existed or not, create a new file and write the text into it
    with open(filename, 'w') as file:
        file.write(text)
        file.close()


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

def get_urls_from_sitemap(url: str) -> dict:
    sitemap_uri = settings.Config().data['site']['sitemap']
    url_sitemap = url + sitemap_uri
    logger = logging.getLogger('app.Scraper')

    response = requests.get(url_sitemap)
    if response.status_code == 200:
        parcala = BeautifulSoup(response.content, "xml")
    else:
        logger.debug(f'Failed to retrieve sitemap: {response.status_code}')
        exit()

    urls_from_xml = {}
    loc_tags = parcala.find_all('loc')

    for loc in loc_tags:
        urls_from_xml[loc.text] = ''

    # Add the root that was passed as parameter just in case
    urls_from_xml[url] = ''

    logger.debug(f'Number of URLs to walk: ' + str(len(urls_from_xml)))
    return urls_from_xml