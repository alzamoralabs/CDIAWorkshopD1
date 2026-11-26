from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
load_dotenv()

llm = ChatOpenAI(
    model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
    api_key=os.environ.get("OPENAI_API_KEY"),
    temperature=0
)

print(llm.invoke("What is the capital of France?").content)