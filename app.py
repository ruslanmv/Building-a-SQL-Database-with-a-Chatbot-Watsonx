import os
from getpass import getpass
from dotenv import load_dotenv
from langchain_ibm import WatsonxLLM
from langchain.prompts import PromptTemplate
from backend import validate_data, save_data_to_db   # Import backend functions

# Load environment variables
load_dotenv()

# Function to set environment variables
def set_env(var: str):
       env_var = os.getenv(var)
       if not env_var:
               env_var = getpass(f"{var}: ")
               os.environ[var] = env_var
       return env_var

# Load environment variables from .env file
api_key = os.getenv("WATSONX_API_KEY")
project_id = os.getenv("PROJECT_ID")
url = os.getenv("WATSONX_URL")

# Define parameters for the Watsonx model
parameters = {
       "decoding_method": "sample",
       "max_new_tokens": 4095,
       "min_new_tokens": 1,
       "temperature": 0.5,
       "top_k": 50,
       "top_p": 1,
}

# Initialize the WatsonxLLM model
watsonx_llm = WatsonxLLM(
       model_id="meta-llama/llama-3-70b-instruct",
       apikey=api_key,
       url=url,
       project_id=project_id,
       params=parameters,
)

# Define the system prompt
system_prompt = (
       "You are an AI language model designed to assist users by asking a series of medical questions. "
       "After each question, validate the user's response and, if incorrect, ask them to try again up to three times. "
       "Once the user answers correctly, send the response to the backend and move on to the next question."
)

# Initialize the prompt template
prompt_template = PromptTemplate(input_variables=[], template=system_prompt)

# Combine the system prompt with the user's prompt
def create_full_prompt(user_prompt: str) -> str:
       return f"{system_prompt}\n\n{user_prompt}"

# Function to interact with WatsonxLLM model
def ask_watsonx(user_prompt: str) -> str:
       response = watsonx_llm.invoke(create_full_prompt(user_prompt))
       return response

# Function to ask a series of questions
def ask_medical_questions():
       # Predefined list of medical questions
       questions = [
               "Do you have a history of diabetes? (Yes/No)",
               "When was your last medical check-up? (YYYY-MM-DD)",
               "Are you currently taking any medications? (If yes, list them)"
       ]
      
       user_id = 12345
       responses = {}
      
       # Iterate through the list of questions
       for idx, question in enumerate(questions):
               attempts = 0
               while attempts < 3:
                       print(f"Question {idx + 1}: {question}")
                       user_response = input("Answer: ")

                       # Validate the response using Watsonx LLM
                       validation_prompt = f"Is '{user_response}' a valid answer for the question: '{question}'?"
                       validation_response = ask_watsonx(validation_prompt)
                      
                       if "valid" in validation_response.lower():
                               responses[f"question_{idx + 1}"] = user_response
                               break
                       else:
                               attempts += 1
                               print("That response doesn't seem right. Please try again.")
              
               if attempts == 3:
                       print(f"Skipping to the next question after 3 failed attempts for: '{question}'")

       # Validate the final set of responses
       if validate_data(responses):
               # Save data to the database
               save_data_to_db(user_id, responses)
               print("Data successfully saved.")
       else:
               print("The data provided is invalid.")

       print("Thank you for completing the questionnaire. Have a great day!")

# Start the chatbot interaction
if __name__ == "__main__":
       ask_medical_questions()