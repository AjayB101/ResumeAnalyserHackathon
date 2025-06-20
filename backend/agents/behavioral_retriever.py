import os
import json
from typing import List
import uuid
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.retrievers import TavilySearchAPIRetriever
from newspaper import Article
from interiew_prompts.prompts import InterviewPrompts
from langchain_community.vectorstores import Chroma
from llm_client import llm
from dotenv import load_dotenv

# Fix for protobuf issue
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

load_dotenv()

# --- Scrape web pages ---
def scrape_text(url: str) -> str:
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
        return ""

# --- Get URLs using TavilySearchAPIRetriever ---
def retrieve_behavioral_urls(query: str, k: int = 5) -> List[str]:
    try:
        retriever = TavilySearchAPIRetriever(k=k)
        docs = retriever.invoke(query)
        return [d.metadata.get("source", d.metadata.get("url")) for d in docs]
    except Exception as e:
        print(f"Error retrieving URLs: {e}")
        return []

# --- Setup persistent Chroma DB using alternative embeddings ---
def setup_chroma_from_urls(urls: List[str], persist_dir="behavioral_chroma_db") -> Chroma:
    if not urls:
        print("No URLs provided, creating empty vectorstore")
        # Create a dummy document to avoid empty vectorstore
        documents = [Document(page_content="Behavioral interview questions focus on past experiences and how candidates handled specific situations.", metadata={"source": "default"})]
    else:
        documents = []
        for url in urls:
            content = scrape_text(url)
            if content.strip():
                documents.append(Document(page_content=content, metadata={"source": url}))
        
        if not documents:
            # Fallback if no content was scraped
            documents = [Document(page_content="Behavioral interview questions focus on past experiences and how candidates handled specific situations.", metadata={"source": "default"})]

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(documents)

    # Try different embedding options
    try:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        print("Using Google embeddings")
    except Exception as e:
        print(f"Google embeddings failed: {e}")
        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            print("Using HuggingFace embeddings as fallback")
        except Exception as e:
            print(f"HuggingFace embeddings failed: {e}")
           

    vectorstore = Chroma.from_documents(
        chunks,
        embedding=embeddings,
        persist_directory=persist_dir
    )
    vectorstore.persist()
    return vectorstore

# --- Final QA agent using RAG ---
def get_behavioral_patterns(job_description: str) -> dict:
    try:
        # Create search query for behavioral interview questions
        search_query = f"behavioral interview questions {job_description}"
        urls = retrieve_behavioral_urls(search_query)
        
        vectorstore = setup_chroma_from_urls(urls)
        retriever = vectorstore.as_retriever(search_type="similarity", k=5)

        # Modified prompt template that works with RetrievalQA
        behavioral_prompt_template = """
You are a helpful interview coach with access to relevant behavioral interview information.

Use the following context from behavioral interview resources to generate relevant questions:

{context}

Based on the context above and the following job description, return 5 behavioral questions and quality sample answers:

Job Description: {question}

Format your response strictly in JSON:
{{
  "questions": [
    {{
      "question": "Tell me about a time when you had to work under pressure to meet a deadline.",
      "sample_answer": "In my previous role, I had to complete a critical project presentation with only 24 hours notice. I prioritized the most important slides, delegated research tasks to team members, and worked through the night to ensure quality. The presentation was successful and led to securing a major client.",
      "source": "behavioral_interview_guide"
    }}
  ]
}}

Important: Output only the JSON object. No preamble or explanation.
"""
        
        # Create the prompt template with the correct variable names
        prompt = PromptTemplate(
            template=behavioral_prompt_template,
            input_variables=["context", "question"]  # RetrievalQA uses 'question' not 'job_description'
        )
        
        # Create the RetrievalQA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": prompt}
        )
        
        # Run the chain with the job description - RetrievalQA expects a string input
        result = qa_chain.run(job_description)
        
        # Try to parse as JSON
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            print("Failed to parse JSON, trying to extract it")
            # Try to find JSON in the response
            result_str = str(result)
            start = result_str.find('{')
            end = result_str.rfind('}')
            if start != -1 and end != -1:
                try:
                    return json.loads(result_str[start:end+1])
                except:
                    pass
            
            print("Could not extract JSON, returning fallback")
            return get_fallback_questions()
            
    except Exception as e:
        print(f"Error in get_behavioral_patterns: {e}")
        return get_fallback_questions()

def get_fallback_questions() -> dict:
    return {
        "questions": [
            {
                "question": "Tell me about a time you faced a challenging situation at work and how you handled it.",
                "sample_answer": "I once had to manage a project with a tight deadline when a key team member fell ill. I redistributed tasks, communicated transparently with stakeholders about potential delays, and worked extra hours to ensure quality delivery. We completed the project on time and learned valuable lessons about resource planning.",
                "source": "fallback"
            },
            {
                "question": "Describe a situation where you had to work with a difficult team member.",
                "sample_answer": "I worked with a colleague who was resistant to new processes. I took time to understand their concerns, addressed them directly, and showed how the changes would benefit the team. By involving them in the solution design, I gained their buy-in and improved team collaboration.",
                "source": "fallback"
            },
            {
                "question": "Tell me about a time you had to learn something new quickly.",
                "sample_answer": "When our company adopted a new software system, I had 48 hours to become proficient before training others. I used online tutorials, practiced with sample data, and created quick reference guides. I successfully trained 15 team members and became the go-to person for questions.",
                "source": "fallback"
            },
            {
                "question": "Describe a time when you had to make a decision without complete information.",
                "sample_answer": "During a product launch, we discovered a potential issue but had limited time to investigate fully. I gathered available data, consulted with experts, weighed risks and benefits, and made a decision to proceed with additional monitoring. The launch was successful and the issue never materialized.",
                "source": "fallback"
            },
            {
                "question": "Tell me about a time you received constructive criticism and how you handled it.",
                "sample_answer": "My manager pointed out that my presentations needed more visual elements. Instead of being defensive, I asked for specific suggestions, took a design course, and practiced with colleagues. My next presentation was much more engaging and I received positive feedback from the executive team.",
                "source": "fallback"
            }
        ]
    }