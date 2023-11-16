from scraper.scraper import Scraper
import os
import sys

"""
MAIN
This is the entry point for the scraper

Usage: app.py <config_file>
"""
if __name__ == '__main__':

    if len(sys.argv) > 1:
        filename = sys.argv[1]

        # check if the tmp directory exists, if not create it
        if not os.path.exists('./tmp'):
            os.makedirs('./tmp')

        scraper = Scraper(filename)
        scraper.scrape_site(scraper.get_config().get_root_url_to_scrape())

else:
    print("No configuration xml provided. Please provide a filename as an argument.")
