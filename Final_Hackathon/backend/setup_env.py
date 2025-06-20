#!/usr/bin/env python3
"""
Setup script to configure environment for the payroll system
"""

import os

def create_env_file():
    """Create .env file with the provided API key"""
    
    env_content = """# Google AI Configuration
GOOGLE_API_KEY=AIzaSyAFQFqJu9wRbQjZP_Amh7TvepWBkIJLt68

# Model Configuration
MODEL_NAME=gemini-1.5-flash
TEMPERATURE=0.7
MAX_TOKENS=2048

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173

# MongoDB Configuration
MONGODB_URI=mongodb+srv://divyasihub:yE9dOD0LEn6uUZFY@divyas.bej0utq.mongodb.net/payroll_db

# File Storage
UPLOAD_DIR=data/uploads
OUTPUT_DIR=data/outputs
MAX_FILE_SIZE=10485760  # 10MB

# Security
SECRET_KEY=payroll_hackathon_secret_key_2024_change_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# RAG Configuration
CHROMA_PERSIST_DIRECTORY=data/knowledge_base/chroma_db
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Payroll Configuration
DEFAULT_CURRENCY=INR
DEFAULT_COUNTRY=IN
"""
    
    env_file_path = os.path.join(os.path.dirname(__file__), '.env')
    
    if os.path.exists(env_file_path):
        print(f"⚠️  .env file already exists at {env_file_path}")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("Skipping .env file creation.")
            return
    
    try:
        with open(env_file_path, 'w') as f:
            f.write(env_content)
        print(f"✅ Created .env file at {env_file_path}")
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")

def create_directories():
    """Create necessary directories"""
    
    directories = [
        'data/uploads',
        'data/outputs',
        'data/knowledge_base/tax_rules',
        'data/knowledge_base/compliance',
        'data/knowledge_base/templates',
    ]
    
    for directory in directories:
        dir_path = os.path.join(os.path.dirname(__file__), directory)
        try:
            os.makedirs(dir_path, exist_ok=True)
            print(f"✅ Created directory: {directory}")
        except Exception as e:
            print(f"❌ Failed to create directory {directory}: {e}")

def create_sample_contract():
    """Create a sample contract file for testing"""
    
    sample_contract = """EMPLOYMENT CONTRACT

Employee Information:
- Employee ID: EMP001
- Employee Name: John Doe
- Designation: Software Engineer
- Department: Engineering
- Join Date: 2024-01-15

Salary Structure:
- Basic Salary: 50000 INR
- House Rent Allowance (HRA): 20000 INR
- Leave Travel Allowance (LTA): 8000 INR
- Variable Pay: 10000 INR
- Performance Bonus: 15000 INR
- Other Allowances: 5000 INR

Statutory Obligations:
- Provident Fund (PF)
- Employee State Insurance (ESI)
- Gratuity
- Tax Deducted at Source (TDS)

Terms and Conditions:
1. This is a full-time employment contract
2. Salary will be paid monthly on the 1st of each month
3. All statutory deductions will be applied as per government regulations
4. Performance bonuses are subject to company performance and individual performance
5. HRA is subject to actual rent receipts and tax regulations

This contract is valid from 2024-01-15 and will be reviewed annually.
"""
    
    contract_file_path = os.path.join(os.path.dirname(__file__), 'data/uploads/sample_contract.txt')
    
    try:
        with open(contract_file_path, 'w') as f:
            f.write(sample_contract)
        print(f"✅ Created sample contract at {contract_file_path}")
    except Exception as e:
        print(f"❌ Failed to create sample contract: {e}")

def main():
    """Main setup function"""
    print("🚀 Payroll System Environment Setup")
    print("=" * 50)
    
    print("1. Creating .env file...")
    create_env_file()
    
    print("\n2. Creating directories...")
    create_directories()
    
    print("\n3. Creating sample contract...")
    create_sample_contract()
    
    print("\n" + "=" * 50)
    print("✅ Environment setup completed!")
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Test setup: python test_setup.py")
    print("3. Start server: uvicorn app.main:app --reload")
    print("4. Open: http://localhost:8000/docs")

if __name__ == "__main__":
    main() 