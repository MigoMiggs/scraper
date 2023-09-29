import os
from urllib.parse import urlparse




def get_filename_and_extension(url: str):
    parsed_url = urlparse(url)
    path = parsed_url.path
    filename = os.path.basename(path)
    filename_without_extension, file_extension = os.path.splitext(filename)
    return filename, filename_without_extension, file_extension