
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
import logging.config
import os
import uvicorn
import yaml
from server.kb.KB import KB
from dotenv import load_dotenv, find_dotenv
from langchain.chains import RetrievalQA
from fastapi.middleware.cors import CORSMiddleware
from utilities.utils import get_gpt_model, get_retriever_from_type, get_prompt_for_multianswer


description = """
IBTS Assistant REST API answers questions against knowledge bases built from scraping sites.
"""
config = None

with open('../config/logging.yaml', 'r') as file:
    log_config = yaml.safe_load(file.read())
    logging.config.dictConfig(log_config)

    logger = logging.getLogger('server')
    logger.debug("Logger has been setup")

_ = load_dotenv(find_dotenv())  # read local .env file

@asynccontextmanager
async def lifespan(_app: FastAPI):
    await app_start_up()
    yield
    await app_shutdown()


async def app_start_up() -> None:
    file_path = './settings/server_config.yaml'
    global config

    logger.debug("App startup")


async def app_shutdown():
    logger.debug("App shutdown")
    # foo


def load_config() -> None:
    file_path = './settings/server_config.yaml'
    global config
    global logger

    logger.debug("Config loading has been setup")

    # initialize the configuration
    if config is None:
        # load the config from server_config.yaml

        if not (os.path.exists(file_path)):
            raise Exception("Configuration file not found")

        with open(file_path, 'r') as file:
            config = yaml.safe_load(file)


def load_vector_dbs() -> dict[str, KB]:
    knowledge_bases = config['kbs']
    vectordbs: dict[str, KB] = {}

    kb: dict
    for kb in knowledge_bases:
        the_name: str = kb['name']
        directory: str = kb['directory']
        embeddings_type: str = kb['embeddings']

        vdb: KB
        vdb = KB(the_name, directory, embeddings_type)
        vectordbs[the_name] = vdb

    return vectordbs


def create_app() -> FastAPI:
    load_config()
    _app = FastAPI(
        title="IBTS Assistant REST API",
        description=description,
        summary="Use AI Assisstant to query against knowledge bases.",
        version="0.0.1",
        terms_of_service="http://example.com/terms/",
        contact={
            "name": "IBTS Inc",
            "url": "http://ibts.com",
            "email": "bulug@ibts.com",
        },
        lifespan=lifespan,
    )

    _app.logger = logger
    _app.kbs = load_vector_dbs()
    _app.use_azure = config['use_azure']

    origins = [
        "http://localhost:3000",  # React local dev server
        "https://localhost",
    ]

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return _app


app = create_app()


@app.get("/", tags=["Root"])
async def read_root() -> dict:
    return {"message": "Welcome to IBTS Assistant Web Server!"}


@app.get("/question")
async def get_question(request: Request,
                       question: str,
                       kb: str = 'chroma',
                       llm: str = 'gpt-3.5-turbo'):

    assert isinstance(request.app.kbs, object)
    application = request.app
    stores = application.kbs
    logger = application.logger
    use_azure = application.use_azure

    logger.debug(f"Getting answer to question: {question}")

    # Get the vbs from the dict
    vc = stores[kb].get_db()

    # Show the total documents to make sure we got the right db
    logger.debug(f"Getting answer to question: {question}")

    if vc is None:
        result = "Could not find knowledge base."
        logger.debug("No KB found.")
        return {"answer": result}

    model = get_gpt_model(use_azure, model_name=llm, temperature=0)
    retriever = get_retriever_from_type('standard', vc, k=6, llm=model)

    qa_chain = RetrievalQA.from_chain_type(
        model,
        retriever=retriever
    )

    result = qa_chain({"query": question})
    answer = result['result']

    logger.debug(f'Answer: {answer}')
    return {"answer": answer}

@app.get("/question_answer")
async def get_question_answer(request: Request,
                       question: str,
                       answers: str,
                       kb: str = 'chroma',
                       llm: str = 'gpt-3.5-turbo'):
    application = request.app
    stores = application.kbs
    logger = application.logger
    use_azure = application.use_azure

    logger.debug(f"Getting answer to question: {question}")
    logger.debug(f"Choosing answer from answers: {answers}")

    # Get the vbs from the dict
    vc = stores[kb].get_db()

    # Make sure that our retriever gets back 6 results
    model = get_gpt_model(use_azure, model_name=llm, temperature=0)
    retriever = get_retriever_from_type('standard', vc, k=6, llm=model)

    # Get the prompt for the multi-answer model
    chat_prompt = get_prompt_for_multianswer()

    # Create the chain
    qa_chain = RetrievalQA.from_chain_type(
        model,
        retriever=retriever,
        chain_type_kwargs={
            "prompt": chat_prompt
        },
        return_source_documents=True
    )

    question += '\n\n' + answers
    result = qa_chain({"query": question})
    answer = result['result']

    return {"answer": answer}



if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        reload=True
    )
