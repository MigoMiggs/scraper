from settings import Config
import logging
from langchain.embeddings import HuggingFaceEmbeddings, OpenAIEmbeddings
from langchain.vectorstores import Chroma
import langchain
from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

class VectorDB:
    _instance = None
    vectordb = None
    config = None
    persistance_path = ''
    logger = None
    embeddings: langchain.embeddings = None

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=150
    )

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Loads configuration data from file if not loaded already."""
        if not hasattr(self, 'initialized'):
            self.initialized = True

            self.config = Config('./config.yaml')
            self.persistance_path = self.config.data['vectordb']['chroma-path']
            self.logger = logging.getLogger('app.Scraper')
            self.embeddings: langchain.embeddings

            self.logger.debug("Load embeddings")

            # Set the right kind of embeddings
            if self.config.get_embeddings()["type"] == 'HUGGING_FACE':
                embeddings_model_name = "sentence-transformers/all-MiniLM-L6-v2"
                self.embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)
            elif self.config.get_embeddings()["type"] == 'OPEN_AI':
                self.embeddings = OpenAIEmbeddings()
            else:
                self.logger.error("Unknown embeddings setting.")
                raise Exception("Unknown embeddings setting.")

            self.logger.debug("Embeddings Loaded")
            self.vectordb = Chroma(persist_directory=self.persistance_path, embedding_function=self.embeddings)

    def split_embed_store(self, filename: str, ext: str) -> None:
        self.logger.debug("Split, embed and store " + filename)
        loader = None

        try:
            if ext == '.pdf':
                loader = PyPDFLoader(filename)
                self.logger.debug('Load PDF')
            else:
                loader = TextLoader(filename)
                self.logger.debug('Load Text')

            if loader is not None:
                docs = loader.load_and_split(self.text_splitter)
                self.vectordb.add_documents(documents=docs)
        except Exception as e:
            self.logger.error(f'Failed to split and embed: {filename}')
            self.logger.error(f'Exception: {e}')


    def get_vector_db(self):
        return self.vectordb



