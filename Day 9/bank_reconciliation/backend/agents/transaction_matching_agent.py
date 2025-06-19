from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import pandas as pd
from typing import List, Dict
from config import GOOGLE_API_KEY

class TransactionMatchingAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=GOOGLE_API_KEY,
            temperature=0.7
        )

    def match_transactions(self, bank_df: pd.DataFrame, books_df: pd.DataFrame) -> List[Dict]:
        """Match transactions using LLM-based fuzzy/exact matching"""
        prompt = PromptTemplate(
            input_variables=["bank_transactions", "book_transactions"],
            template="""
            Compare these transactions and find matches:
            Bank Transactions:
            {bank_transactions}
            
            Book Transactions:
            {book_transactions}
            
            Return matches in JSON format with confidence scores.
            """
        )
        bank_str = bank_df.to_string()
        books_str = books_df.to_string()
        response = self.llm.invoke(
            prompt.format(
                bank_transactions=bank_str,
                book_transactions=books_str
            )
        )
        return response 