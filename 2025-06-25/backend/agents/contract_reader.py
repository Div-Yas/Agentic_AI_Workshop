# contract_reader.py
import sys
import fitz  # PyMuPDF
import json
import os
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.2,
    max_output_tokens=1024
)

# MongoDB Setup
MONGO_URI = os.getenv("MONGODB_URI")
client = MongoClient(MONGO_URI)
db = client["payroll_db"]
counter_collection = db["counters"]

def get_next_employee_id():
    """Fetch and increment the employee ID counter in MongoDB"""
    counter = counter_collection.find_one_and_update(
        {"_id": "employee_id"},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True
    )
    return f"EMP{counter['sequence_value']:03d}"  # EMP001, EMP002...

def extract_text_from_pdf(pdf_path):
    """Extract raw text from PDF using PyMuPDF"""
    with fitz.open(pdf_path) as doc:
        text = ""
        for page in doc:
            text += page.get_text()
        return text

def _parse_contract_with_llm(contract_text):
    """Use Gemini LLM to parse contract content into structured JSON"""
    prompt_template = PromptTemplate(
        input_variables=["contract_content"],
        template="""
        Parse this employment contract and extract key information.
        Return ONLY a valid JSON object with the exact structure below:

        {{
            "employee_id": "string",
            "employee_name": "string",
            "designation": "string",
            "department": "string",
            "join_date": "YYYY-MM-DD",
            "salary_components": {{
                "basic_salary": number,
                "hra": number,
                "lta": number,
                "variable_pay": number,
                "bonuses": number,
                "other_allowances": number
            }},
            "statutory_obligations": ["string"],
            "region": "string",
            "currency": "INR"
        }}

        Contract:
        {contract_content}

        Rules:
        - Return ONLY the JSON object, no extra text or markdown.
        - Use INR currency by default.
        - If join_date is missing, use today's date as default.
        """
    )

    try:
        prompt = prompt_template.format(contract_content=contract_text)
        response = llm.invoke(prompt)
        content = response.content.strip()

        # Clean response if wrapped in markdown
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        # Try to parse JSON
        parsed_data = json.loads(content)

        # Generate unique employee ID
        parsed_data["employee_id"] = get_next_employee_id()

        # Ensure defaults
        parsed_data.setdefault("currency", "INR")
        parsed_data["join_date"] = parsed_data.get("join_date", datetime.now().strftime("%Y-%m-%d"))

        return parsed_data

    except Exception as e:
        print(f"[ERROR] Failed to parse contract with LLM: {e}")
        # Fallback to default values
        return {
            "employee_id": get_next_employee_id(),
            "employee_name": "Unknown Employee",
            "designation": "Employee",
            "department": "General",
            "join_date": datetime.now().strftime("%Y-%m-%d"),
            "salary_components": {
                "basic_salary": 50000,
                "hra": 20000,
                "lta": 5000,
                "variable_pay": 0,
                "bonuses": 0,
                "other_allowances": 0
            },
            "statutory_obligations": ["PF"],
            "region": "Karnataka",
            "currency": "INR"
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing file path"}))
        sys.exit(1)

    pdf_path = sys.argv[1]

    try:
        raw_text = extract_text_from_pdf(pdf_path)
        parsed_data = _parse_contract_with_llm(raw_text)
        print(json.dumps(parsed_data, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)