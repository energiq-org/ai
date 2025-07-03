from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

import os

def load_documents(data_path="data"):
    docs = []
    for filename in os.listdir(data_path):
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(data_path, filename))
            pages = loader.load()
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=750,
                chunk_overlap=150,
                separators=["\n\n", "\n", ".", " ", ""]
            )
            chunks = splitter.split_documents(pages)
            for chunk in chunks:
                chunk.metadata["source"] = filename
            docs.extend(chunks)
    return docs

def create_vectorstore(documents):
    embedding_model = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
    vectorstore = Chroma.from_documents(documents, embedding_model, persist_directory="vectorstore")
    vectorstore.persist()
    return vectorstore

def get_retriever():
    embedding_model = OpenAIEmbeddings()
    vectorstore = Chroma(persist_directory="vectorstore", embedding_function=embedding_model)
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    return retriever
