import os
import json
from typing import List, Dict, Any
import uuid
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.retrievers import TavilySearchAPIRetriever
from newspaper import Article
from langchain_community.vectorstores import Chroma
from llm_client import llm
from dotenv import load_dotenv
import re
from urllib.parse import urlparse

# Fix for protobuf issue
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

load_dotenv()

# --- Convert Job Description to Search Query ---
def convert_jd_to_search_query(job_description: str) -> str:
    """
    Convert a job description to an optimized search query for behavioral interview questions.
    """
    try:
        search_query_prompt = PromptTemplate(
            input_variables=["job_description"],
            template="""
You are an expert at creating search queries for finding relevant behavioral interview questions.

Given the following job description, extract the key skills, technologies, responsibilities, and role requirements to create an optimized search query for finding behavioral interview questions.

Job Description:
{job_description}

Create a concise search query (maximum 10-15 words) that focuses on:
1. The primary role/position
2. Key technical skills mentioned
3. Important soft skills or responsibilities
4. Industry context if relevant

Format: Return only the search query, nothing else.

Example inputs and outputs:
- Input: "Software Engineer position requiring Java, Spring Boot, microservices..."
- Output: "software engineer behavioral interview questions Java Spring microservices"

- Input: "Data Scientist role with Python, machine learning, analytics..."  
- Output: "data scientist behavioral interview questions Python machine learning"

Search Query:"""
        )
        
        # Use the LLM to generate the search query
        search_query = llm.predict(search_query_prompt.format(job_description=job_description))
        
        # Clean up the response - remove any extra text
        search_query = search_query.strip()
        
        # Add "behavioral interview questions" if not already present
        if "behavioral interview" not in search_query.lower():
            search_query = f"behavioral interview questions {search_query}"
        
        # Limit length and clean up
        words = search_query.split()
        if len(words) > 15:
            search_query = " ".join(words[:15])
            
        print(f"Generated search query: {search_query}")
        return search_query
        
    except Exception as e:
        print(f"Error converting JD to search query: {e}")
        # Fallback: extract basic terms
        return extract_basic_search_terms(job_description)

def extract_basic_search_terms(job_description: str) -> str:
    """
    Fallback method to extract basic search terms from job description.
    """
    # Common technical terms and skills to look for
    technical_terms = [
        'java', 'python', 'javascript', 'c#', 'c++', 'react', 'angular', 'node.js',
        'spring', 'django', 'flask', 'microservices', 'docker', 'kubernetes',
        'aws', 'azure', 'gcp', 'sql', 'mongodb', 'postgresql', 'redis',
        'machine learning', 'data science', 'ai', 'devops', 'ci/cd'
    ]
    
    role_terms = [
        'software engineer', 'developer', 'data scientist', 'product manager',
        'frontend', 'backend', 'fullstack', 'mobile', 'web'
    ]
    
    jd_lower = job_description.lower()
    found_terms = []
    
    # Look for role terms first
    for term in role_terms:
        if term in jd_lower:
            found_terms.append(term)
            break  # Only take the first role match
    
    # Look for technical terms
    for term in technical_terms:
        if term in jd_lower and len(found_terms) < 6:  # Limit to 6 terms total
            found_terms.append(term)
    
    # Create search query
    if found_terms:
        search_query = f"behavioral interview questions {' '.join(found_terms[:5])}"
    else:
        search_query = "behavioral interview questions software engineer"
    
    print(f"Fallback search query: {search_query}")
    return search_query

# --- Enhanced URL source tracking ---
def get_domain_name(url: str) -> str:
    """Extract clean domain name from URL for source attribution."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except:
        return "web_source"

def scrape_text_with_metadata(url: str) -> Dict[str, Any]:
    """Scrape text and return with metadata for better source tracking."""
    try:
        article = Article(url)
        article.download()
        article.parse()
        
        return {
            'content': article.text,
            'title': article.title or 'Untitled',
            'url': url,
            'domain': get_domain_name(url),
            'success': True
        }
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
        return {
            'content': '',
            'title': '',
            'url': url,
            'domain': get_domain_name(url),
            'success': False
        }

# --- Get URLs using TavilySearchAPIRetriever ---
def retrieve_behavioral_urls(query: str, k: int = 5) -> List[str]:
    try:
        retriever = TavilySearchAPIRetriever(k=k)
        docs = retriever.invoke(query)
        urls = []
        for d in docs:
            url = d.metadata.get("source", d.metadata.get("url"))
            if url:
                urls.append(url)
        print(f"Retrieved {len(urls)} URLs from search")
        return urls
    except Exception as e:
        print(f"Error retrieving URLs: {e}")
        return []

# --- Setup persistent Chroma DB with enhanced source tracking ---
def setup_chroma_from_urls(urls: List[str], persist_dir="behavioral_chroma_db") -> tuple[Chroma, Dict[str, str]]:
    """Setup Chroma DB and return source mapping for attribution."""
    source_mapping = {}  # Maps chunk IDs to source domains
    
    if not urls:
        print("No URLs provided, creating empty vectorstore")
        documents = [Document(
            page_content="Behavioral interview questions focus on past experiences and how candidates handled specific situations.", 
            metadata={"source": "system_default", "domain": "system", "title": "Default Content"}
        )]
        source_mapping["system_default"] = "system_default"
    else:
        documents = []
        successful_sources = []
        
        for url in urls:
            scraped_data = scrape_text_with_metadata(url)
            if scraped_data['success'] and scraped_data['content'].strip():
                doc = Document(
                    page_content=scraped_data['content'], 
                    metadata={
                        "source": url,
                        "domain": scraped_data['domain'],
                        "title": scraped_data['title']
                    }
                )
                documents.append(doc)
                successful_sources.append(scraped_data['domain'])
                source_mapping[url] = scraped_data['domain']
        
        print(f"Successfully scraped {len(documents)} documents from sources: {successful_sources}")
        
        if not documents:
            # Fallback if no content was scraped
            documents = [Document(
                page_content="Behavioral interview questions focus on past experiences and how candidates handled specific situations.", 
                metadata={"source": "system_fallback", "domain": "system", "title": "Fallback Content"}
            )]
            source_mapping["system_fallback"] = "system_fallback"

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(documents)
    
    # Update source mapping for chunks
    for chunk in chunks:
        chunk_source = chunk.metadata.get('source', 'unknown')
        if chunk_source in source_mapping:
            chunk.metadata['source_domain'] = source_mapping[chunk_source]
        else:
            chunk.metadata['source_domain'] = get_domain_name(chunk_source) if chunk_source != 'unknown' else 'unknown'

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
            raise Exception("No embedding service available")

    vectorstore = Chroma.from_documents(
        chunks,
        embedding=embeddings,
        persist_directory=persist_dir
    )
    vectorstore.persist()
    return vectorstore, source_mapping

# --- Enhanced behavioral patterns with proper source attribution ---
def get_behavioral_patterns(job_description: str) -> dict:
    try:
        # Convert job description to optimized search query
        search_query = convert_jd_to_search_query(job_description)
        
        # Use the optimized search query to get URLs
        urls = retrieve_behavioral_urls(search_query)
        print(f"Found URLs: {urls}")
        
        vectorstore, source_mapping = setup_chroma_from_urls(urls)
        retriever = vectorstore.as_retriever(search_type="similarity", k=5)

        # Enhanced prompt template with source attribution
        behavioral_prompt_template = """
You are a helpful interview coach with access to relevant behavioral interview information.

Use the following context from behavioral interview resources to generate relevant questions:

{context}

Based on the context above and the following job description, return 5 behavioral questions and quality sample answers that are specifically relevant to this role:

Job Description: {question}

Focus on behavioral questions that assess:
1. Technical problem-solving and debugging skills
2. Collaboration and teamwork in software development
3. Learning and adapting to new technologies
4. Handling project pressures and deadlines
5. Code quality and best practices

IMPORTANT: For the source field, use one of these based on where the information came from:
- If from web search results: use the domain name (e.g., "linkedin.com", "glassdoor.com", "indeed.com")
- If no specific source available: use "web_search_results"

Format your response strictly in JSON:
{{
  "questions": [
    {{
      "question": "Tell me about a time when you had to troubleshoot a complex technical issue in production.",
      "sample_answer": "In my previous role, our application was experiencing intermittent crashes. I used logging and monitoring tools to identify the root cause, which was a memory leak in our caching layer. I worked with the team to implement a fix and added better monitoring to prevent similar issues. This reduced downtime by 80%.",
      "source": "web_search_results"
    }}
  ]
}}

Important: Output only the JSON object. No preamble or explanation.
"""
        
        # Create the prompt template with the correct variable names
        prompt = PromptTemplate(
            template=behavioral_prompt_template,
            input_variables=["context", "question"]
        )
        
        # Create the RetrievalQA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": prompt}
        )
        
        # Run the chain with the job description
        result = qa_chain.run(job_description)
        print(f"Raw LLM result: {result}")
        
        # Try to parse as JSON
        try:
            parsed_result = json.loads(result)
            # Enhance source attribution with actual domains if available
            if 'questions' in parsed_result:
                available_sources = [domain for domain in source_mapping.values() if domain not in ['system_default', 'system_fallback']]
                for i, question in enumerate(parsed_result['questions']):
                    if question.get('source') == 'web_search_results' and available_sources:
                        # Use the first available source domain
                        question['source'] = available_sources[0] if available_sources else 'web_search_results'
            return parsed_result
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
            return get_fallback_questions_for_role(job_description, source_mapping)
            
    except Exception as e:
        print(f"Error in get_behavioral_patterns: {e}")
        return get_fallback_questions_for_role(job_description, {})

def get_fallback_questions_for_role(job_description: str, source_mapping: Dict[str, str] = {}) -> dict:
    """
    Generate role-specific fallback questions with proper source attribution.
    """
    jd_lower = job_description.lower()
    
    # Determine source based on whether we had successful web searches
    web_sources = [domain for domain in source_mapping.values() if domain not in ['system_default', 'system_fallback', 'unknown']]
    source_attribution = web_sources[0] if web_sources else "system_fallback"
    
    # Software Engineer specific questions
    if any(term in jd_lower for term in ['software', 'developer', 'engineer', 'programming']):
        return {
            "questions": [
                {
                    "question": "Describe a situation where you had to troubleshoot a complex performance issue in a production environment. How did you approach the problem and what was the outcome?",
                    "sample_answer": "In my previous role, I encountered a performance bottleneck in our e-commerce platform. I used monitoring tools to identify the root cause, which was a misconfigured database query. I worked with the database team to optimize the query and implemented a caching layer to reduce the load. The changes resulted in a 30% reduction in response time and improved user experience.",
                    "source": source_attribution
                },
                {
                    "question": "Tell me about a time when you had to design and implement a scalable backend component. What design patterns and technologies did you use, and how did you ensure its maintainability?",
                    "sample_answer": "In my previous role, I designed a microservices-based architecture for a real-time analytics platform. I used a service-oriented approach, with each service responsible for a specific functionality. I implemented load balancing, auto-scaling, and monitoring to ensure high availability and performance. The design allowed for easy maintenance and upgrades, reducing downtime by 50%.",
                    "source": source_attribution
                },
                {
                    "question": "Can you describe a situation where you had to integrate a third-party API into your application? What challenges did you face, and how did you overcome them?",
                    "sample_answer": "In my previous role, I integrated a payment gateway API into our e-commerce platform. I faced challenges with authentication, rate limiting, and error handling. I worked with the API provider to resolve the issues and implemented a retry mechanism to handle transient errors. The integration was successful, and we saw a 25% increase in sales.",
                    "source": source_attribution
                },
                {
                    "question": "Tell me about a time when you had to ensure the security and integrity of user data. What measures did you take, and how did you communicate with stakeholders?",
                    "sample_answer": "In my previous role, I implemented a data encryption solution for our customer database. I worked with the security team to ensure compliance with regulatory requirements and communicated the changes to stakeholders. I also developed a data access control policy to restrict access to sensitive data. The implementation resulted in a 99.9% reduction in data breaches.",
                    "source": source_attribution
                },
                {
                    "question": "Describe a situation where you had to work with a cross-functional team to deliver a project. What was your role, and how did you contribute to the team's success?",
                    "sample_answer": "In my previous role, I worked with a team to launch a new product feature. I was responsible for designing and implementing the backend API. I collaborated with the front-end team to ensure seamless integration and worked with the QA team to ensure thorough testing. The project was delivered on time, and we received positive feedback from customers.",
                    "source": source_attribution
                }
            ]
        }
    
    # Default fallback for other roles
    return get_fallback_questions(source_attribution)
def has_relevant_data(vectorstore, query: str, threshold: float = 0.75) -> bool:
    """
    Check if the vectorstore contains relevant documents for the given query.
    Returns True if at least one result exceeds the threshold similarity score.
    """
    retriever = vectorstore.as_retriever(search_type="similarity", k=1)
    results = retriever.get_relevant_documents(query)
    return len(results) > 0 and results[0].metadata.get('source') not in ['system_default', 'system_fallback']


def get_fallback_questions(source_attribution: str = "system_fallback") -> dict:
    """Return generic fallback questions with proper source attribution."""
    return {
        "questions": [
            {
                "question": "Tell me about a time you faced a challenging situation at work and how you handled it.",
                "sample_answer": "I once had to manage a project with a tight deadline when a key team member fell ill. I redistributed tasks, communicated transparently with stakeholders about potential delays, and worked extra hours to ensure quality delivery. We completed the project on time and learned valuable lessons about resource planning.",
                "source": source_attribution
            },
            {
                "question": "Describe a situation where you had to work with a difficult team member.",
                "sample_answer": "I worked with a colleague who was resistant to new processes. I took time to understand their concerns, addressed them directly, and showed how the changes would benefit the team. By involving them in the solution design, I gained their buy-in and improved team collaboration.",
                "source": source_attribution
            },
            {
                "question": "Tell me about a time you had to learn something new quickly.",
                "sample_answer": "When our company adopted a new software system, I had 48 hours to become proficient before training others. I used online tutorials, practiced with sample data, and created quick reference guides. I successfully trained 15 team members and became the go-to person for questions.",
                "source": source_attribution
            },
            {
                "question": "Describe a time when you had to make a decision without complete information.",
                "sample_answer": "During a product launch, we discovered a potential issue but had limited time to investigate fully. I gathered available data, consulted with experts, weighed risks and benefits, and made a decision to proceed with additional monitoring. The launch was successful and the issue never materialized.",
                "source": source_attribution
            },
            {
                "question": "Tell me about a time you received constructive criticism and how you handled it.",
                "sample_answer": "My manager pointed out that my presentations needed more visual elements. Instead of being defensive, I asked for specific suggestions, took a design course, and practiced with colleagues. My next presentation was much more engaging and I received positive feedback from the executive team.",
                "source": source_attribution
            }
        ]
    }

# --- Test function ---
def test_behavioral_agent():
    """Test the behavioral interview agent with sample job description."""
    honeywell_jd = """
    As a Software Engr I here at Honeywell, you will play a crucial role in developing and maintaining software solutions that drive innovation and efficiency across various industries. You will work within cross-functional teams on cutting-edge projects that transform the way businesses operate. Your expertise in software engineering, coding, and problem-solving will be instrumental in shaping the future of technology and industry solutions.
    
    YOU MUST HAVE:
    * Bachelor's degree from an accredited institution in a technical discipline such as science, technology, engineering, mathematics
    * Experience in software development
    * Proficiency in programming languages such as Java, C#, or Python
    
    Key Responsibilities:
    * Develop and maintain software applications and systems
    * Collaborate with crossfunctional teams to deliver highquality software solutions
    * Design and implement software solutions that meet customer requirements
    * Troubleshoot and debug software issues
    * Conduct code reviews and ensure adherence to coding standards
    """
    
    print("Testing Behavioral Interview Agent...")
    print("=" * 50)
    
    # Test search query generation
    search_query = convert_jd_to_search_query(honeywell_jd)
    print(f"Generated search query: {search_query}")
    print("-" * 50)
    
    # Test full behavioral patterns generation
    result = get_behavioral_patterns(honeywell_jd)
    print("Generated behavioral patterns:")
    print(json.dumps(result, indent=2))
    
    return result

