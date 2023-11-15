import os
from urllib.parse import urlparse, urlunparse
import logging
import requests
from bs4 import BeautifulSoup
from langchain.chat_models import ChatOpenAI, AzureChatOpenAI
from urllib.parse import quote, unquote
import re

from langchain.prompts.chat import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate
)

def get_gpt_model(use_azure, model_name, temperature=0):
    llm_model = None
    if use_azure:
        llm_model = AzureChatOpenAI(
            openai_api_base=os.getenv("OPENAI_API_AZURE_BASE"),
            openai_api_version=os.getenv("OPENAI_API_AZURE_VERSION"),
            deployment_name="dev-gpt-35-turbo-16k",
            openai_api_key=os.getenv("OPENAI_API_AZURE_KEY"),
            openai_api_type="azure",
            temperature=temperature
        )
    else:
        llm_model = ChatOpenAI(model_name=model_name, temperature=0)

    return llm_model


def get_retriever_from_type(retriever_type: str, vs, k: int = 6, llm=None):
    retriever = None
    if retriever_type == 'standard':

        retriever = vs.as_retriever(search_type="similarity", search_kwargs={"k": 6})
    elif retriever_type == 'multi_query':

        retriever = MultiQueryRetriever.from_llm(
            retriever=vs.as_retriever(search_kwargs={"k": 6}), llm=llm
        )

    return retriever


def get_filename_and_extension(url: str):
    '''
    Get the filename and extension from a URL
    :param url:
    :return:
    '''
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
    """
    Transform a URL into a filename that can be used on disk without any issues
    :param url:
    :return:
    """
    # Strip out the 'http://' or 'https://' part
    parsed_url = urlparse(url)
    stripped_url = parsed_url.netloc + parsed_url.path

    # Replace dots with underscores
    url_with_underscores = stripped_url.replace('.', '_')

    # Replace slashes with dashes
    transformed_url = url_with_underscores.replace('/', '__')

    return transformed_url


def transform_url_reverse(url: str) -> str:
    """
    Replaces a safe filename with a URL

    :param url:
    :return:
    """

    # Replace underscores with dots
    url_with_dots = url.replace('_', '.')

    # Replace dashes with slashes
    transformed_url = url_with_dots.replace('__', '/')
    return transformed_url


def normalize_url(url):
    parsed_url = urlparse(url)
    # Reconstruct the URL without the query and fragment components
    normalized_url = urlunparse(
        (parsed_url.scheme, parsed_url.netloc, parsed_url.path, None, None, None)
    )
    return normalized_url


def get_urls_from_sitemap(url_sitemap: str) -> dict:
    logger = logging.getLogger('app.Scraper')

    urls_from_xml = {}
    response = requests.get(url_sitemap)
    if response.status_code == 200:
        parcala = BeautifulSoup(response.content, "xml")
    else:
        logger.debug(f'Failed to retrieve sitemap: {response.status_code}')
        return urls_from_xml

    loc_tags = parcala.find_all('loc')

    for loc in loc_tags:
        urls_from_xml[loc.text] = ''

    logger.debug(f'Number of URLs to walk: ' + str(len(urls_from_xml)))
    return urls_from_xml


def url_to_filename(url: str) -> str:
    """Converts a URL to a safe filename."""
    return quote(url, safe='')


def filename_to_url(filename: str) -> str:
    """Converts a safe filename back to its original URL."""
    return unquote(filename)


def parse_assessment_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Split content by '-----' to separate different Q&A blocks
    qa_blocks = re.split(r'-----\n', content)

    data = []
    for block in qa_blocks:
        lines = block.strip().split('\n')
        question_id, question, answers = None, None, ""

        # Iterate through each line to find the question and answers
        for i, line in enumerate(lines):
            if line.startswith('Question:'):
                # Find the next non-empty line after 'Question:'
                for potential_question_line in lines[i + 1:]:
                    if potential_question_line.strip():  # Ensure it's not an empty line
                        question_id_match = re.match(r'(\d+[a-zA-Z]?)\.\s+(.*)', potential_question_line)
                        if question_id_match:
                            question_id = question_id_match.group(1)
                            question = question_id_match.group(2)
                        break
            elif line.startswith('Answers:'):
                # The answers start after 'Answers:' line
                for answer_line in lines[i + 1:]:
                    if answer_line.strip() and not answer_line.startswith('-----'):
                        answers += answer_line.strip() + '\n'
                    else:
                        # If an empty line or '-----' is encountered, stop adding to answers
                        break

        # Make sure we have found a question and its answers
        if question_id and question and answers:
            data.append({
                'question_id': question_id,
                'question': question,
                'answers': answers.strip()  # Remove any trailing whitespace
            })

    return data


def get_prompt_for_multianswer():
    system_template = """" \
    Instructions:
    * You are an evaluator that knows about Natural Disaster Recovery. \
    * User will provider a multiple choice question and the possible answers below. \
    * You will pick the best answer based on the included pieces of context. The questions \
    will always go from 1 - 6, the 6th answer is always "I don't know." 
    * Answers 1 - 5 will go from low to high, from the perspecive of how good \
    the adherence is to the provided question. 
    * These questions and answers are used for Natural Disaster Readiness. \
    * The Community Resilience Assessment Framework and Tools (CRAFT) \
    * Equitable Climate Resilience (ECR) platform is a resource for cities to assess and strengthen their resilience - \
    the ability to to mitigate, respond to, and recover from crises. Also, after the answer, you will explain how you got to the answer, \ 
    referrring to the pieces of context that gave you the answer. \n\
    -------------------- \n\
    Context:
    {context}
    """
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)

    human_template = """ {question} """
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    return chat_prompt
