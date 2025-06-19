from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
import os
from dotenv import load_dotenv
from config import GOOGLE_API_KEY

load_dotenv()

class ReconciliationKnowledgeAgent:
    def __init__(self):
        # Initialize embeddings
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        # Initialize vector store
        self.vector_store = Chroma(
            collection_name="reconciliation_knowledge",
            embedding_function=self.embeddings
        )
        
        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=GOOGLE_API_KEY,
            temperature=0.7,
            convert_system_message_to_human=True
        )
        
        # Initialize QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(),
            return_source_documents=True
        )
    
    def add_documents(self, documents):
        """Add documents to the vector store."""
        self.vector_store.add_documents(documents)
    
    def query(self, question: str) -> str:
        """Query the knowledge base with a question."""
        result = self.qa_chain({"query": question})
        return result["result"] 