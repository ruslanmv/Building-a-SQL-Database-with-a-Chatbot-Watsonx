## Building a Watsonx LLM-Powered Chatbot with Backend Integration in Python: A Step-by-Step Guide

In this blog post, we will build a **Watsonx LLM-powered chatbot** that asks users a series of medical questions, validates their responses, and saves the data securely in a MySQL database. The key feature of this solution is that you only need to run a single script (`app.py`), which will handle both the frontend (chatbot) and the backend (data validation, encryption, and database storage) seamlessly.

### Table of Contents
1. Overview of the Solution
2. Project Structure
3. Frontend (app.py): Chatbot Powered by Watsonx LLM
4. Backend (backend.py): Data Validation and SQL Database Integration
5. How to Run the Application
6. Conclusion

---

### 1. **Overview of the Solution**

The goal of this project is to build a simple chatbot that:
- Asks a series of medical questions.
- Validates the user’s answers using **IBM Watsonx LLM**.
- Stores the validated answers securely in a MySQL database after encrypting sensitive data.

The chatbot will give users up to **three attempts** to provide a valid answer to each question. If the user fails to answer correctly after three tries, the chatbot moves on to the next question. After all the questions are answered, the validated responses are encrypted and stored in a MySQL database.

### 2. **Project Structure**

We will divide the project into two main Python files:
- **app.py**: This will handle the frontend chatbot and interact with the user.
- **backend.py**: This will handle the backend logic, including validation, encryption, and saving data to the SQL database.

Here's the high-level architecture of the solution:
1. **Frontend (Chatbot)**: Powered by IBM Watsonx, it asks and validates medical questions.
2. **Backend**: Performs data validation, encryption, and stores the data in the database.
3. **MySQL Database**: Stores the encrypted user responses securely.

---

### 3. **Frontend (app.py): Chatbot Powered by Watsonx LLM**

The `app.py` script is the entry point to the application. It powers the chatbot that interacts with the user and validates their responses using **IBM Watsonx LLM**. It then sends the validated responses to the backend for storage.

Here’s the full code for `app.py`:

```python
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
```

### Key Features:
- **Watsonx LLM Integration**: The chatbot uses IBM Watsonx to validate user responses in real-time.
- **Three Attempts Per Question**: The user has up to three attempts to provide a valid answer before the chatbot moves on to the next question.
- **Backend Integration**: Once the answers are validated, they are passed to the backend for storage in the database.

---

### 4. **Backend (backend.py): Data Validation and SQL Database Integration**

The `backend.py` file contains the logic to validate, encrypt, and save the data to an SQL database. It handles the secure storage of the user's medical data.

Here’s the full code for `backend.py`:

```python
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from cryptography.fernet import Fernet
from datetime import datetime

# Define SQLAlchemy base
Base = declarative_base()

# Define SQLAlchemy model for the medical history table
class MedicalHistory(Base):
       __tablename__ = 'medical_history'
      
       id = Column(Integer, primary_key=True)
       user_id = Column(Integer, nullable=False)
       diabetes = Column(String(255), nullable=False)
       last_checkup = Column(String(255), nullable=False)
       medications = Column(Text, nullable=True)

# Replace with your actual SQL server connection details
DATABASE_URI = "mysql+pymysql://user:password@127.0.0.1/medical_db"
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

# Generate an encryption key (in production, this should be stored securely)
ENCRYPTION_KEY = Fernet.generate_key()
cipher_suite = Fernet(ENCRYPTION_KEY)

# Function to encrypt sensitive data
def encrypt_data(data):
       encrypted_data = {}
       for key, value in data.items():
               encrypted_data[key] = cipher_suite.encrypt(value.encode()).decode()
       return encrypted_data

# Function to validate the input data
def validate_data(answers):
       if 'question_1' not in answers or answers['question_1'] not in ['Yes', 'No']:
               return False
       if 'question_2' in answers and not valid_date(answers['question_2']):
               return False
       return True

# Helper function to check if a string is a valid date
def valid_date(date_str):
       try:
               datetime.strptime(date_str, "%Y-%m-%d")
               return True
       except ValueError:
               return False

# Function to save the data to the database
def save_data_to_db(user_id, answers):
       # Encrypt sensitive data
       encrypted_data = encrypt_data(answers)

       # Save to the database
       new_record = MedicalHistory(
               user_id=user_id,
               diabetes=encrypted_data.get('question_1'),
               last_checkup=encrypted_data.get('question_2'),
               medications=encrypted_data.get('question_3')
       )

       session.add(new_record)
       session.commit()

       return True
```

### Key Features:
- **Data Validation**: Ensures that the data follows a valid format (e.g., checking if the date is in the correct format).
- **Encryption**: Sensitive data (e.g., medical history) is encrypted using **Fernet encryption** before storing it in the database.
- **SQLAlchemy Integration

### Key Features (Continued):

- **Data Validation**:
   - The `validate_data()` function ensures that the answers provided by the user follow the correct format.
   - For example, it checks if the response to the question "Do you have a history of diabetes?" is either "Yes" or "No."
   - Similarly, it checks whether the "last medical check-up" date is provided in a valid `YYYY-MM-DD` format.
 
- **Encryption**:
   - The `encrypt_data()` function uses **Fernet encryption** from the `cryptography` library to encrypt sensitive data such as medical history before storing it in the database.
   - Each answer is encrypted before insertion into the database, ensuring that the data remains secure.

- **SQLAlchemy Integration**:
   - The `save_data_to_db()` function inserts the encrypted data into the SQL database using **SQLAlchemy**. The table schema is defined using the **MedicalHistory** model, which stores fields such as `user_id`, `diabetes`, `last_checkup`, and `medications`.
   - SQLAlchemy ORM (Object Relational Mapping) is used to map Python objects to database records, making it easier to interact with the database.

---

### 5. **How to Run the Application**

Follow these steps to run the full application on your machine.

#### Step 1: **Install Required Packages**

First, you need to install the required Python libraries. You can install them using `pip`:

```bash
pip install sqlalchemy cryptography pymysql langchain_ibm python-dotenv
```

- **SQLAlchemy**: For database interaction.
- **Cryptography**: For encrypting sensitive data before saving to the database.
- **PyMySQL**: MySQL connector for Python.
- **Langchain_ibm**: To integrate with IBM Watsonx LLM.
- **Python-dotenv**: To load environment variables (for API keys, database credentials, etc.).

#### Step 2: **Set Up Your MySQL Database**

You need to create a MySQL database to store the encrypted medical history data. Here's how you can create the database and table:

1. **Log in to MySQL** and create a new database (e.g., `medical_db`):
   ```sql
   CREATE DATABASE medical_db;
   ```

2. **Create the `medical_history` table** inside the database:
   ```sql
   USE medical_db;

   CREATE TABLE medical_history (
       id INT AUTO_INCREMENT PRIMARY KEY,
       user_id INT NOT NULL,
       diabetes VARCHAR(255) NOT NULL,
       last_checkup VARCHAR(255) NOT NULL,
       medications TEXT
   );
   ```

#### Step 3: **Set Up Environment Variables**

Create a `.env` file in the root of your project to store your **IBM Watsonx API keys** and **MySQL credentials**. This file will be loaded by the `dotenv` package in both `app.py` and `backend.py`.

Here’s an example `.env` file:

```
WATSONX_API_KEY=your_watsonx_api_key
PROJECT_ID=your_project_id
WATSONX_URL=https://api.your_watsonx_instance.com
```

Make sure to replace the values with your actual credentials.

#### Step 4: **Run the Application**

You can now run the application by simply executing the `app.py` file. This will start the chatbot, interact with the user, validate the responses, and save the data to the SQL database.

```bash
python app.py
```

#### Interaction Flow:

1. **The chatbot asks the user three medical questions**:
   - "Do you have a history of diabetes?" (Yes/No)
   - "When was your last medical check-up?" (YYYY-MM-DD)
   - "Are you currently taking any medications?"
  
2. **User responses are validated**:
   - The chatbot gives the user up to three attempts to provide a valid answer.
  
3. **Data is securely stored**:
   - Once all answers are validated, the data is encrypted and stored in the MySQL database.

---

### 6. **Conclusion**

In this blog, we have built a fully integrated chatbot powered by **IBM Watsonx LLM** that can ask medical questions, validate responses, and securely store user data in a MySQL database. The solution is simple to deploy, requiring only a single Python script to be run. The architecture is modular, with a clear separation of concerns between the frontend chatbot (`app.py`) and the backend processing (`backend.py`).

### Key Features of the Solution:
- **Real-time Response Validation**: IBM Watsonx LLM ensures that user responses are valid before storing them.
- **Data Encryption**: Sensitive medical data is encrypted using **Fernet encryption** from the `cryptography` library before being stored in the SQL database.
- **Database Integration**: The solution uses **SQLAlchemy ORM** to easily map Python objects to database tables and store data securely.

### Future Enhancements:
- **Add More Questions**: You can easily extend the chatbot to ask additional questions based on your requirements.
- **Deploy the Solution**: You can deploy this solution on a web server and turn it into a web-based chatbot for real-world applications.
- **Enhanced NLP**: You can integrate additional NLP techniques for more complex validation logic, especially when handling natural language responses.

By using **IBM Watsonx**, **SQLAlchemy**, and **Fernet encryption**, we have created a secure, interactive, and user-friendly chatbot solution that can be used for data collection in sensitive environments such as healthcare.
