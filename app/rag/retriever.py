from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
import os

class Retriever:
    def __init__(self, data_dir="app/rag/data"):
        self.embeddings = OpenAIEmbeddings(openai_api_key=os.getenv('OPENAI_API_KEY'))
        self.vectorstore = self._load_vectorstore(data_dir)
    
    def _load_vectorstore(self, data_dir):
        loader = DirectoryLoader(data_dir, glob="**/*.txt")
        documents伟

System: documents = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_documents(documents)
        return FAISS.from_documents(chunks, self.embeddings)
    
    def search(self, query):
        return self.vectorstore.similarity_search(query, k=3)