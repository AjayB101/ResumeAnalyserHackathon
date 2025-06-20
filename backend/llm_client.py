from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()
llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)

if __name__=="__main__":
    res=llm.invoke("What is ai")
    print(res)