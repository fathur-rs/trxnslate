import os
from functools import lru_cache
from typing import Dict, Generator

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from openai import OpenAI
import logging

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(name)s - %(message)s", level=logging.INFO)

class Llama3_1_70B:
    BASE_URL = "https://integrate.api.nvidia.com/v1"
    MODEL = "meta/llama3-70b-instruct"
    
    QUESTION_TEMPLATE = """
    Tolong jelaskan resep medis ini:
    - Jelaskan fungsi obat
    - Jelaskan cara penggunaan nya yang tertera pada resep yang diberikan
    - Jelaskan dosis nya yang tertera pada resep yang diberikan

    Instruksi Output:
    - output dalam bahasa Indonesia 
    - output sebagai paragraph (tidak ada bullet point dan number point)
    """

    PROMPT_TEMPLATE = """
    Jawab pertanyaan berdasarkan input yang diberikan saja.
    Harap berikan jawaban yang paling akurat berdasarkan pertanyaan tersebut.
    Harap menggunakan bahasa yang formal.
    Harap tidak ragu-ragu dalam menjawab, percaya diri saja!!!.
    
    Context:
    {context}
    
    Question: {input}
    """

    def __init__(self):
        load_dotenv()
        self.client = self._create_client()
        self.chat_prompt_template = ChatPromptTemplate.from_template(self.PROMPT_TEMPLATE)

    @lru_cache(maxsize=1)
    def _create_client(self) -> OpenAI:
        return OpenAI(
            base_url=self.BASE_URL,
            api_key=os.environ['NVIDIA_API_KEY']
        )

    def generate_prompt(self, context: str) -> str:
        return self.chat_prompt_template.format(context=context, input=self.QUESTION_TEMPLATE)

    def get_response(self, prompt: str) -> str:
        completion = self._stream_completion(prompt)
        return ''.join(completion)

    def _stream_completion(self, prompt: str) -> Generator[str, None, None]:
        completion = self.client.chat.completions.create(
            model=self.MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=1024,
            stream=True
        )

        for chunk in completion:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    def analyze_prescription(self, prescription_text: str) -> str:
        prompt = self.generate_prompt(prescription_text)
        return self.get_response(prompt)