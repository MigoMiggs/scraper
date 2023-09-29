import os
import utils
from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
import openai


def read_kb_filenames() -> list:
    files = os.listdir('./scraped')
    loaders = []
    counter = 0
    for f in files:
        filename, filename_without_extension, file_extension = utils.get_filename_and_extension(f)
        counter = counter + 1

        if (file_extension == '.pdf'):
            # loaders.append(PyPDFLoader('./scraped/' + f))
            print(filename)
        else:
            loaders.append(TextLoader('./scraped/' + f))

    return loaders


if __name__ == '__main__':
    openai.api_key = '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'

    embedding = OpenAIEmbeddings()
    persist_directory = './chroma/'

    loaders = read_kb_filenames()
    docs = []
    counter = 0;

    print("loading")
    for loader in loaders:
        docs.extend(loader.load())
        counter = counter + 1
        print(counter)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=150
    )

    print("splitting")
    splits = text_splitter.split_documents(docs)
    print(len(splits))
    vectordb = Chroma.from_documents(
        documents=splits,
        embedding=embedding,
        persist_directory=persist_directory
    )


    print('loaded these many collections: ' + str(vectordb._collection.count()))

