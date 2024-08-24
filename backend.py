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