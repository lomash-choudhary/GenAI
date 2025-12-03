from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# this will create our path something like this 05_RAG_1/nodejs.pdf

pdf_file_path = Path(__file__).parent / "backend-roadmap.pdf"

# loading the pdf data

loader = PyPDFLoader(file_path=pdf_file_path)

docs = loader.load() #this will load the file from the file path page by page. it is an array of documents.

# print("DOC [5]", docs[5])

# next step we will do the chunking of this data

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1000, #here chunk size means that we should get each chunk of 1000-1000 characters
    chunk_overlap = 400
)

split_docs = text_splitter.split_documents(documents=docs)

# Vector Embeddings.
embedding_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", google_api_key=os.getenv("GEMINI_API_KEY"))

# using [embedding_model] create embeddings of [split_docs] and store it in DB
vector_store = QdrantVectorStore.from_documents(
    documents=split_docs,
    url="http://localhost:6333",
    collection_name="learning_rag",
    embedding=embedding_model
)

print("Indexing of embedding model done...")
