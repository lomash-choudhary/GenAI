from pathlib import Path
from dotenv import load_dotenv
from exceptiongroup import catch
from openai import OpenAI, api_key
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
import time


load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# this will create our path something like this 05_RAG_1/nodejs.pdf

pdf_file_path = Path(__file__).parent / "nodejs.pdf"

# loading the pdf data

loader = PyPDFLoader(file_path=pdf_file_path)

docs = loader.load() #this will load the file from the file path page by page. it is an array of documents.

# print("DOC [5]", docs[5])

# next step we will do the chunking of this data

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 10000, #here chunk size means that we should get each chunk of 1000-1000 characters
    chunk_overlap = 400
)

split_docs = text_splitter.split_documents(documents=docs)

# Vector Embeddings.
embedding_model = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", google_api_key=os.getenv("GEMINI_API_KEY"))

# using [embedding_model] create embeddings of [split_docs] and store it in DB

batch_size = 10 #it will process 10 chunks at a time
delay_seconds = 20 #this gives a delay of 20 seconds between batches.

for i in range(0, len(split_docs), batch_size):
    batch = split_docs[i:i+batch_size]
    print(f"processing batch {i//batch_size + 1}...")

    try:
        vector_store = QdrantVectorStore.from_documents(
        documents=split_docs,
        url="http://localhost:6333",
        collection_name="learning_rag",
        embedding=embedding_model
        )
        print(f"✅ Indexed batch {i//batch_size + 1}")
    except Exception as e:
        print(f"❌ Error: {e}")

    print(f"⏳ Waiting {delay_seconds}s before next batch...")
    time.sleep(delay_seconds)


print("Indexing of embedding model done...")
