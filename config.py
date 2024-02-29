from os import getenv
from dotenv import load_dotenv
from dotenv.main import find_dotenv
import os

load_dotenv(find_dotenv())

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY_LOCAL")
LLM_MODEL = os.getenv("LLM_MODEL")