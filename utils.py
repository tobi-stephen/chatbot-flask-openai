import logging
import json
from dotenv import load_dotenv

import fitz
import requests
from bs4 import BeautifulSoup
from langchain_openai import OpenAI, ChatOpenAI
from langchain.prompts import PromptTemplate


logger = logging.getLogger(__name__)
load_dotenv()  # needed to run load the OPENAI api key from .env


class Chain:
    def __init__(self, subject, source=None, resource = None):
        self.subject = subject
        self.resource = resource
        self.source = source
        self.setup_llm_chain()

    def setup_llm_chain(self):
        logger.info(f'setting up llm chain for {self.subject} from {self.source}')
        
        if not self.source:
            context = ''
        elif self.source == 'file':
            context = extract_text_from_pdf(self.resource, 'context_data.txt')
        elif self.source == 'url':
            context = extract_text_from_web(self.resource, 'context_data.txt')
        else:
            raise ValueError(f'unsupported source type: {self.source}')    

        assistant_template = context + '''
        You are an AI assistant for {subject}, named Mr. Zen. Your expertise is in providing advice
        about anything related to {subject}. This includes any general {subject} related queries.
        You are only providing information within this scope.
        If asked a question that is not about {subject}, respond with, "I am unable to help with this".
        Question: {question}
        Answer: 
        '''

        assistant_prompt_template = PromptTemplate(input_variables=['question', 'subject'], template=assistant_template)
        # llm = OpenAI(model='gpt-3.5-turbo-instruct', temperature=0)
        llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            # api_key="...",  # if you prefer to pass api key in directly instaed of using env vars
            # base_url="...",
            # organization="...",
            # other params...
        )
        self.chain = assistant_prompt_template | llm
        
    def invoke(self, question):
        response = self.chain.invoke({'question': question, 'subject': self.subject})
        json_response = json.loads(response.json())
        return json_response['content']


def extract_text_from_pdf(pdf_file_path, out_path):
    logger.info('extracting text from pdf')

    pdf_text = ''
    try:
        with (
            fitz.open(filename=pdf_file_path) as doc,
            open(file=out_path, mode='w', encoding='utf-8') as out_f
        ):
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                pdf_text += page.get_textpage().extractText()
            out_f.write(pdf_text)
    except Exception as e:
        logger.error(f'error reading pdf: {e}')
        raise ValueError('extraction error')
    
    logger.info('text extraction successful')
    return pdf_text


def extract_text_from_web(target_url, out_path):
    logger.info('extracting text from web')
    
    web_text = ''
    response = requests.get(target_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        for paragraph in soup.find_all('p'):
            web_text += paragraph.get_text()
    
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(web_text)
    else:
        logger.error(f'invalid response: {response.status_code}')
        raise ValueError('extraction error')
    
    logger.info('text extraction successful')
    return web_text


if __name__=='__main__':
    try:
        logging.basicConfig(level=logging.INFO)
        resource = 'https://www.landonhotel.com'
        subject = 'Landon Hotel'
        source = 'url'
        chain = Chain(subject=subject, source=source, resource=resource)
        
        # testing the chatbot logic in a running loop
        question = 'Hello'
        while True:
            response = chain.invoke({'question': question, 'subject': subject})
            logger.info(f'[[{response}]]')
            question = input('>')
        
    except KeyboardInterrupt:
        pass
