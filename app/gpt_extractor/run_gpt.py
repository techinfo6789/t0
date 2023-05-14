from langchain.llms import OpenAI
from langchain.chains import LLMChain
import PyPDF2
from langchain import PromptTemplate
from app.doc_reader.doc2text import DocReader

class GPTExtractor:

    def __init__(self, api_key, model_name):
        self.api_key = api_key
        self.model_name = model_name
        self.llm = OpenAI(model_name = self.model_name, temperature =0, openai_api_key = self.api_key)
        
    
    def entity_extractor(self, pdf_text, prompt_template):

        gpt_template = prompt_template + """PDF Text: {pdf_text}"""

        PROMPT = PromptTemplate(template = gpt_template, input_variables=["pdf_text"])

        chain = LLMChain(llm = self.llm, prompt = PROMPT)

        return chain.run(pdf_text = pdf_text)