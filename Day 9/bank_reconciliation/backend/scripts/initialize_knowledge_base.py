from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from agents.reconciliation_knowledge_agent import ReconciliationKnowledgeAgent
import os

def initialize_knowledge_base():
    # Initialize the agent
    agent = ReconciliationKnowledgeAgent()
    
    # Get the path to the knowledge base directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    knowledge_base_dir = os.path.join(current_dir, '..', '..', 'data', 'knowledge_base')
    
    # Load all text files from the knowledge base directory
    loader = DirectoryLoader(knowledge_base_dir, glob="**/*.txt", loader_cls=TextLoader)
    documents = loader.load()
    
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(documents)
    
    # Add documents to the vector store
    agent.add_documents(chunks)
    
    print("Knowledge base initialized successfully!")

if __name__ == "__main__":
    initialize_knowledge_base() 