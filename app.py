from scraper.scraper import Scraper
from utilities.utils import filename_to_url

"""
MAIN
This is the entry point for the scraper
"""
if __name__ == '__main__':
    scraper = Scraper('./config_cdc.yaml')
    scraper.scrape_site(scraper.get_config().get_root_url_to_scrape())

    #site = filename_to_url('https%3A%2F%2Fwww.orlando.gov%2FPublic-Safety%2FOFD%2FBecome-an-Orlando-Firefighter')
    #scraper.scrape(site)

    # scraper.scrape('https://www.orlando.gov/files/sharedassets/public/v/3/departments/oca/22_oca_mmg-applicationguidelines-schoolsandnpo-june2022.pdf')
    # scraper.scrape('https://www.orlando.gov/files/sharedassets/public/departments/edv/main-streets/sodo2.jpeg')
    #scraper.scrape('https://www.fema.gov/press-release/20210318/fema-awards-florida-department-health-nearly-11-million-hurricane-irma')
