import json
from langchain import OpenAI, PromptTemplate
from langchain.chains import LLMChain
from langchain.chains.summarize import load_summarize_chain
from langchain.document_loaders import PyPDFLoader
import logging
from langchain.chains import AnalyzeDocumentChain
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler  # for streaming response
from langchain.callbacks.manager import CallbackManager
from constants import (
    MODEL_ID,
    MODEL_BASENAME,
    MAX_NEW_TOKENS,
    MODELS_PATH,
)
from datetime import datetime
import os
today_date = datetime.now().strftime("%B %d, %Y")
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

from langchain.vectorstores import Chroma
os.environ["TOGETHER_API_KEY"] = "1cecf43792b1187b044ab0293853353cc45caf8fdfe0a82e049d53cbf5954d26"
import together

# set your API key
together_api_key = os.environ["TOGETHER_API_KEY"]

llm = Together(
    model="togethercomputer/llama-2-70b-chat",
    temperature=0.7,
    max_tokens=128,
    top_k=1,
    together_api_key=together_api_key
)

file_path = "user_chat/User.txt"
# Function to categorize user based on chat history
def categorize_user(file_path):

    try:
        with open(file_path, 'r') as file:
            text_data = file.read()
    except FileNotFoundError:
        print("File not found. Please check the file path.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
  
    from langchain.chains.question_answering import load_qa_chain

    qa_chain = load_qa_chain(llm, chain_type="map_reduce")

    qa_document_chain = AnalyzeDocumentChain(combine_docs_chain=qa_chain)
    prompt = """Analyse the given chat history between the user and the HR AI assistant chatbot. Categoriese the user into one of the following categories:
     1. Formal communicator
      2. Informal communicator
       3. Detailed communicator
         4. Guided interactor
          5. Varied feedback provider
           6. Autonomous decision maker
              Based on the categorisation only output the exact category to the user. If the user cannot be categorised into the given output categories, output the category as 'Cannot be categorised'.
               Example: 1) chat history analysis shows that the user is an Autonomous decision maker. Output: Autonomous decision maker
             2) chat history analysis shows that the user is an informal communicator. Output: Informal communicator"""
    response = qa_document_chain.run(input_document=text_data, question=prompt)
        # Extract and return the category from the model's response
    category = response
    return category

def enhance_user_query(user_query):
    # Construct a prompt for the language model to enhance the user's query
    template = """Enhance the user query to produce a refined query for a Human Resources (HR) chatbot. The goal is to retrieve accurate information from a chatbot powered by a large language model. Ensure that the enhanced query maintains the user's original purpose and intended context. The refined query should effectively communicate the user's inquiry to the HR chatbot while optimizing for clarity and relevance.: {user_query}"""
    prompt=PromptTemplate.from_template(template)
    llm_chain = LLMChain(prompt=prompt, llm=llm)
    # Use the language model to generate an enhanced query
    enhanced_query = llm_chain(user_query)
    return enhanced_query


def set_system_prompt(category):
    # Define your default system prompt
    default_prompt = f"""You are athenaHR, an HR assistance chatbot designed for Quadwave employees. Your primary objective is to promptly aid and address inquiries related to human resources only based on the context provided to you. Deliver concise and accurate responses. Do not provide any information on your own. The chat history provided to you is solely to help you maintain coherence in your responses. Do not use it as a reference to provide information. If you cannot answer a user question based on the provided context, inform the user. Do not present any information to the user if you don't think it is relevant.The chat history is given to you to maintain coherence in your responses. Do not use any the chat history for new inferences. Use only parts of the context that is relevant to the current query and ensure you are not accidentally reanswering or accounting for questions in the chat history. Today is {today_date}.
    Example: 
    Query: what is the start and end dates of thimy family floater insurance policy.
    AthenaHR: Hello! Your family floater insurance policy started on May 14, 2023, and it will expire on May 13, 2024.
    Query: I want to know the details of maternity benefits covered in the insurance policy.
    AthenaHR: Hello! The maternity benefits in your policy cover the first two deliveries. Additionally, the third and fourth child are covered, but subject to twins or triplets in the second delivery only. Pre-natal and post-natal expenses are covered within the maternity limit on in-patient department (IPD) expenses.
    Query: When is the next holiday?
    AthenaHR: Based on today's date and the holiday calendar, the next holiday is on December 25, 2023 for christmas."""
  # Map category to a custom prompt (add more categories as needed)
    category_to_prompt = {
        "Formal communicator": f"You are athenaHR, the HR assistant for Quadwave employees. Your user is a Formal Communicator who values professionalism in communication. Provide information in a formal and business-appropriate manner, maintaining a tone of respect and formality.Today is {today_date}",
        "Informal communicator": f"You are athenaHR, the friendly HR chatbot for Quadwave employees. Your user is an Informal Communicator who appreciates a more casual and conversational tone. Feel free to engage in friendly banter while delivering helpful HR information.Today is {today_date}",
        "Detailed communicator": f"You are athenaHR, an HR assistance chatbot designed for Quadwave employees. Your user prefers detailed and thorough information. Take the time to provide comprehensive responses, ensuring all aspects of the inquiry are covered. Prioritize depth and clarity in your explanations.Today is {today_date}",
        "Guided interactor": f"You are athenaHR, the HR assistant for Quadwave employees. Your user is a Guided Interactor who appreciates step-by-step guidance. Assist them by breaking down information into manageable steps. Offer structured support to help them navigate through HR processes effectively.Today is {today_date}",
        "Varied feedback provider": f"You are athenaHR, the HR assistant for Quadwave employees. Your user is a Varied Feedback Provider, offering different styles of feedback. Be receptive to both direct critiques and constructive suggestions. Adapt your responses to accommodate a range of feedback approaches.Today is {today_date}",
        "Autonomous decision maker": f"Your user is an Autonomous Decision Maker who prefers making decisions independently. Provide information that allows them to make confident decisions on their own. Offer guidance without overwhelming details.Today is {today_date}",
    }

    # Check if each category is present in the response
    for category_to_check in category_to_prompt.keys():
        if category_to_check.lower() in category.lower():
            return category_to_prompt[category_to_check]

    # If none of the categories are present, return the default prompt
    return default_prompt

def get_system_prompt():    
    file_path="user_chat/User.txt"
    category = categorize_user(file_path)
    system_prompt = set_system_prompt(category)
    return system_prompt

def main(file_path):
   # file_path = "user_chat/User.txt"
   # category = categorize_user(file_path)
   # print(category)
    #system_prompt = set_system_prompt(category)
   # print("System Prompt:")
   # print(system_prompt)
    user_query = input("\nEnter a query: ")
    query = enhance_user_query(user_query)
    #query = enhanced_query['text']
    print("Enhanced Query:", query)
    #llm = load_model(device_type='mps', model_id=MODEL_ID, model_basename=MODEL_BASENAME, LOGGING=logging)
    #user_query = input("\nEnter a query: ")
    #enhanced_query = enhance_user_query(user_query)
    #print("Enhanced Query:", enhanced_query)


if __name__ == "__main__":
    main(file_path=file_path)