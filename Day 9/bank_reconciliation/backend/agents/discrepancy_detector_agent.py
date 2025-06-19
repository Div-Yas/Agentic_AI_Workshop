from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import pandas as pd
from typing import List, Dict
from config import GOOGLE_API_KEY
import json
import re

class DiscrepancyDetectorAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=GOOGLE_API_KEY,
            temperature=0.7
        )

    def detect_unreconciled_items(self, bank_df: pd.DataFrame, books_df: pd.DataFrame, matches: List[Dict]) -> List[Dict]:
        """Detects unreconciled items and provides initial reasons using LLM"""
        prompt = PromptTemplate(
            input_variables=["bank_df", "books_df", "matches"],
            template="""
            Analyze these transactions. Identify any items from Bank Transactions or Book Transactions that are not found in the Current Matches.
            For each identified unreconciled item, provide a brief reason for the discrepancy (e.g., missing, date mismatch, amount mismatch).
            
            Bank Transactions:
            {bank_df}
            
            Book Transactions:
            {books_df}
            
            Current Matches:
            {matches}
            
            Return the unreconciled items and their reasons in JSON format. Each item in the list should include:
            - "bank_transaction_id" (if from bank) or "book_transaction_id" (if from books)
            - "description"
            - "amount"
            - "type" (e.g., "missing_in_books", "missing_in_bank", "amount_mismatch")
            - "reason"
            - "bank_amount" (for amount mismatches)
            - "book_amount" (for amount mismatches)
            
            Example of expected JSON format:
            {{
                "unreconciled_items": [
                    {{
                        "bank_transaction_id": "BANK123",
                        "book_transaction_id": "BOOK123",
                        "description": "Payment to Vendor",
                        "type": "amount_mismatch",
                        "bank_amount": -100.00,
                        "book_amount": -150.00,
                        "reason": "Amount mismatch: Bank shows -100.00, Book shows -150.00"
                    }}
                ]
            }}
            """
        )
        llm_response = self.llm.invoke(
            prompt.format(
                bank_df=bank_df.to_string(),
                books_df=books_df.to_string(),
                matches=str(matches)
            )
        )
        
        json_string = llm_response.content.strip()
        if json_string.startswith('```json'):
            json_string = json_string[len('```json'):]
        if json_string.endswith('```'):
            json_string = json_string[:-len('```')]
        json_string = json_string.strip()

        json_match = re.search(r'(\{.*\}|\[.*\])', json_string, re.DOTALL)
        if json_match:
            json_string = json_match.group(1)
        else:
            print(f"No valid JSON object or array found in LLM response for Discrepancy Detector: {json_string}")
            return []

        try:
            parsed_json = json.loads(json_string)
            if isinstance(parsed_json, dict):
                return parsed_json.get("unreconciled_items", [])
            elif isinstance(parsed_json, list):
                return parsed_json
            else:
                return []
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON for Discrepancy Detector from LLM: {e}")
            print(f"Problematic JSON string for Discrepancy Detector: {json_string}")
            return []

    def detect(self, bank_df, books_df, matches, unmatched_bank, unmatched_books):
        discrepancies = []
        # Unmatched bank entries
        for idx in unmatched_bank:
            discrepancies.append({
                "type": "missing_in_books",
                "bank_row": bank_df.loc[idx].to_dict(),
                "reason": "No matching entry in books"
            })
        # Unmatched book entries
        for idx in unmatched_books:
            discrepancies.append({
                "type": "missing_in_bank",
                "book_row": books_df.loc[idx].to_dict(),
                "reason": "No matching entry in bank"
            })
        # Mismatches in matches
        for match in matches:
            if match['score'] < 100:
                discrepancies.append({
                    "type": "fuzzy_match",
                    "bank_row": bank_df.loc[match['bank_index']].to_dict(),
                    "book_row": books_df.loc[match['book_index']].to_dict(),
                    "reason": f"Fuzzy match with score {match['score']}"
                })
        return discrepancies 