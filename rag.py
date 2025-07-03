from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

from helpers.rag_helper import *

load_dotenv()

documents = load_documents()
create_vectorstore(documents)
retriever = get_retriever()


def rag(message: str, retriever=retriever):
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""
        You are a helpful assistant. Use the following context to answer the question.
        If you don't know the answer, say you don't know.

        Context:
        {context}

        Question:
        {question}
        """
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",  
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt},
    )
    
    return qa_chain(message)["result"]

if __name__ == "__main__":
    message = "tell me about the charging types and connectors"
    print(rag(message))