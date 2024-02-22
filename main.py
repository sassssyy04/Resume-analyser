import os
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.chains import HypotheticalDocumentEmbedder
from datetime import datetime
import getpass
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CohereRerank
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.vectorstores import FAISS
from langchain.retrievers import BM25Retriever, EnsembleRetriever
from ingest import load_documents
from langchain.retrievers.document_compressors import LLMChainFilter
from langchain.retrievers import ContextualCompressionRetriever
import click
import torch
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler  # for streaming response
from langchain.callbacks.manager import CallbackManager

callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

from constants import (
    EMBEDDING_MODEL_NAME,
    PERSIST_DIRECTORY,
    MODEL_ID,
    MODEL_BASENAME,
    MAX_NEW_TOKENS,
    MODELS_PATH,
    SOURCE_DIRECTORY
)

os.environ["TOGETHER_API_KEY"] = "1cecf43792b1187b044ab0293853353cc45caf8fdfe0a82e049d53cbf5954d26"
import together

# set your API key
together_api_key = os.environ["TOGETHER_API_KEY"]
# get a new token: https://dashboard.cohere.ai/
cohere_api_key = "rzK5qLPOZtVAQFChoMNz8pkekO0nZfH4aEXVrViL"

os.environ["COHERE_API_KEY"] = cohere_api_key

from langchain.llms import Together
today_date = datetime.now().strftime("%B %d, %Y")
def handle_greetings(query):
    greetings = ["hi", "hello", "hey", "greetings", "morning", "afternoon", "evening"]
    return any(greeting == query.lower() for greeting in greetings)

def get_prompt_template():
        system_prompt= f"""You are a Resume analyser. You are provided with contents from a resume and you  need to answer the following questions based on the contents of the resume."""
        B_INST, E_INST = "[INST]", "[/INST]"
        B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"
        SYSTEM_PROMPT = B_SYS + system_prompt + E_SYS
        instruction = """
        Current Query: {question}
        Current Context: {context}
        chat_history for reference: {chat_history}"""

        prompt_template = B_INST + SYSTEM_PROMPT + instruction + E_INST
        prompt = PromptTemplate(input_variables=["chat_history", "context", "question"], template=prompt_template)
        memory = ConversationBufferMemory(input_key="question", memory_key="chat_history")
        return prompt, memory


device_type = "cuda" if torch.cuda.is_available() else "cpu"



llm = Together(
        model="togethercomputer/llama-2-70b-chat",
        temperature=0.1,
        max_tokens=512,
        top_k=30,
        top_p=0.95,
        together_api_key=together_api_key
    )

embeddings = HuggingFaceInstructEmbeddings(model_name=EMBEDDING_MODEL_NAME, model_kwargs={"device": device_type})
   # embeddings = HypotheticalDocumentEmbedder.from_llm(llm,
    #                                               bge_embeddings,
     ##                                             )         # uncomment the following line if you used HuggingFaceEmbeddings in the ingest.py
            # embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

            # load the vectorstore

new_db = FAISS.load_local("faiss_index", embeddings)
FAISS_retriever = new_db.as_retriever(search_type="similarity_score_threshold", search_kwargs={"score_threshold": .35})
FAISS_retriever2 = new_db.as_retriever(search_type="similarity_score_threshold", search_kwargs={"score_threshold": .5})
        #bm25_retriever = BM25Retriever.from_texts(texts)
        #bm25_retriever.k = 2
ensemble_retriever = EnsembleRetriever(retrievers=[ FAISS_retriever, FAISS_retriever2],
                                            weights=[0.5, 0.5])
compressor = CohereRerank()
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor, base_retriever=ensemble_retriever
)


prompt, memory = get_prompt_template()

def retrieval_qa_pipline(device_type):
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",  # try other chains types as well. refine, map_reduce, map_rerank
        retriever=compression_retriever,
        return_source_documents=True,  # verbose=True,
        callbacks=callback_manager,
        chain_type_kwargs={"prompt": prompt ,"memory": memory}
       )
    return qa

def main():
    qa = retrieval_qa_pipline(device_type)


    while True:
            query = input("\nEnter a query: ")
            if query == "exit":
                break

            if handle_greetings(query):
                print("Hello! I am AthenaHR, here to assist you with any queries you may have related to Human resources within the company.")
                continue
            # Get the answer from the chain
            chat_history = []
            chat_history_text = []  
            if chat_history:

                res = qa({"question": query, "chat_history": chat_history}) 
            else:
                # If chat history is empty, initialize it and make the first query
                res = qa(query)

            # Extract the result
            answer, docs = res["result"], res["source_documents"]
            #chat_history_text.append({"question": query, "answer": answer})
            #chat_history = chat_history_text[-1:]

            print("Query:", query)
            print("Answer:", answer)
    # Get today's date in the format you want


if __name__ == "__main__":
    main()
