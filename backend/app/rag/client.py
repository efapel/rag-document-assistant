import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Shared OpenAI client for embeddings and answer generation
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
