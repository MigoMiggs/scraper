import yaml
import logging.config

class Config:
    """
    Config class for loading and accessing configuration data.

    This class is designed as a singleton to ensure that configuration data
    is loaded from the YAML file only once during the runtime of the program,
    reducing file IO and ensuring consistency across the system.

    Attributes:
        data (dict): A dictionary holding the configuration data.

    Usage:
        config = Config('config.yaml')
        db_config = config.get_db_config()
    """

    _instance = None  # Singleton instance reference
    filepath = ''
    _logger = None

    def __new__(cls, file_path = './config.yaml') :
        """
        Ensures a single instance of Config is created
        :param file_path:
        """
        if not cls._instance:
            cls._instance = super().__new__(cls)
            # File path is stored in the instance to allow re-loading if necessary.
            cls._instance.file_path = file_path
        return cls._instance

    def __init__(self, file_path = './config.yaml'):
        """Loads configuration data from file if not loaded already."""
        if not hasattr(self, 'initialized'):
            self._load_config(file_path)
            self.initialized = True

            # Set the logger
            with open('logging.yaml', 'r') as file:
                log_config = yaml.safe_load(file.read())
                logging.config.dictConfig(log_config)

            if self._logger == None:
                self._logger = logging.getLogger('app.Scraper')
                self._logger.debug("Logger set")

    def _load_config(self, file_path):
        """Loads configuration data from the specified YAML file."""
        with open(file_path, 'r') as file:
            self.data = yaml.safe_load(file)

    def get_embeddings(self):

        return self.data['embeddings']

    def get_logging_config(self):
        return self.data['logging']

    def get_open_ai_key(self):
        return self.data['openai']['key']

    def get_root_url_to_scrape(self):
        return self.data['site']['url']

    def getLogger(self):
        return self._logger