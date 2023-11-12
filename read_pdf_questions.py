import re
import PyPDF2
from scraper.utilities.utils import write_text_to_file

def extract_questions_from_pdf(pdf_path):
    # Read PDF
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in range(len(reader.pages)):
            text += reader.pages[page].extract_text()

    write_text_to_file('test2.txt', text)

    # Pattern to match questions and their options
    pattern = re.compile(r'Q\d+\..*?(?=Q\d+\.|$)', re.DOTALL)
    matches = pattern.findall(text)

    questions = []
    for match in matches:
        # Split question from its options
        question_parts = match.split('\n\n', 1)
        if len(question_parts) == 2:
            question, options = question_parts
            questions.append({
                'question': question.strip(),
                'options': options.strip().split('\n')
            })

    return questions


pdf_path = "test-data/Orlando Pre-Assessment.pdf"
questions = extract_questions_from_pdf(pdf_path)
for q in questions:
    print(q['question'])
    print(q['options'])
    print('-' * 20)
