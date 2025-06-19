from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import pandas as pd
from typing import List, Dict
from config import GOOGLE_API_KEY
from dotenv import load_dotenv
from agents.transaction_matching_agent import TransactionMatchingAgent
from agents.discrepancy_detector_agent import DiscrepancyDetectorAgent
from agents.auto_fix_suggestion_agent import AutoFixSuggestionAgent
import json
import re

class BankReconciliation:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=GOOGLE_API_KEY,
            temperature=0.7
        )
        self.transaction_matching_agent = TransactionMatchingAgent()
        self.discrepancy_detector_agent = DiscrepancyDetectorAgent()
        self.auto_fix_suggestion_agent = AutoFixSuggestionAgent()
        
    def load_data(self, bank_statement_path: str, books_path: str) -> tuple:
        """Load bank statement and books data"""
        bank_df = pd.read_csv(bank_statement_path)
        books_df = pd.read_csv(books_path)
        return bank_df, books_df
    
    def fuzzy_match_transactions(self, bank_df: pd.DataFrame, books_df: pd.DataFrame) -> List[Dict]:
        """Match transactions using the TransactionMatchingAgent"""
        llm_response = self.transaction_matching_agent.match_transactions(bank_df, books_df)
        print(f"Raw LLM response: {llm_response}")  # Debug print
        
        # Extract the content string from the LLM response object
        json_string = llm_response.content.strip()
        print(f"JSON string after strip: {json_string}")  # Debug print
        
        # Remove markdown triple backticks and 'json' prefix if present
        if json_string.startswith('```json'):
            json_string = json_string[len('```json'):]
        if json_string.endswith('```'):
            json_string = json_string[:-len('```')]
        json_string = json_string.strip()
        print(f"JSON string after removing markdown: {json_string}")  # Debug print

        # Use regex to find the first JSON object or array in the string
        json_match = re.search(r'(\{.*\}|\[.*\])', json_string, re.DOTALL)
        if json_match:
            json_string = json_match.group(1)
            print(f"JSON string after regex match: {json_string}")  # Debug print
        else:
            print(f"No valid JSON object or array found in LLM response (matches): {json_string}")
            return []

        try:
            parsed_json = json.loads(json_string)
            print(f"Parsed JSON: {parsed_json}")  # Debug print
            if isinstance(parsed_json, dict):
                matches = parsed_json.get("matches", [])
                print(f"Extracted matches from dict: {matches}")  # Debug print
                return matches
            elif isinstance(parsed_json, list):
                print(f"Returning list directly: {parsed_json}")  # Debug print
                return parsed_json
            else:
                print(f"Unexpected JSON type: {type(parsed_json)}")  # Debug print
                return []
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from LLM (matches): {e}")
            print(f"Problematic JSON string (matches): {json_string}")
            return []
    
    def process_match_reconciliation(self, bank_df: pd.DataFrame, books_df: pd.DataFrame) -> Dict:
        """Process only matched transactions"""
        matches = self.fuzzy_match_transactions(bank_df, books_df)
        print(f"Matches from fuzzy_match_transactions: {matches}")  # Debug print
        return {"matches": matches if isinstance(matches, list) else []}

    def process_unmatched_reconciliation(self, bank_df: pd.DataFrame, books_df: pd.DataFrame, matches: List[Dict]) -> Dict:
        """Process unreconciled transactions using the DiscrepancyDetectorAgent"""
        unreconciled_items = self.discrepancy_detector_agent.detect_unreconciled_items(bank_df, books_df, matches)
        # Ensure we return a dictionary with unreconciled items
        if isinstance(unreconciled_items, list):
            return {"unreconciled": unreconciled_items}
        else:
            return {"unreconciled": []}

    def process_suggestions_for_fixes(self, bank_df: pd.DataFrame, books_df: pd.DataFrame, matches: List[Dict]) -> List[Dict]:
        """Generate auto-fix suggestions for unreconciled items"""
        # First, detect unreconciled items
        unreconciled_items = self.discrepancy_detector_agent.detect_unreconciled_items(bank_df, books_df, matches)
        
        auto_fixes = []
        for discrepancy in unreconciled_items:
            print(f"Processing discrepancy (type: {type(discrepancy)}, content: {discrepancy})")
            suggestion = self.auto_fix_suggestion_agent.suggest_fixes(discrepancy)
            auto_fixes.append({
                "discrepancy": discrepancy,
                "suggestion": suggestion
            })
        return auto_fixes

    def process_reconciliation(self, bank_statement_path: str, books_path: str) -> Dict:
        """Main reconciliation process"""
        # Load data
        bank_df, books_df = self.load_data(bank_statement_path, books_path)
        
        # Find matches
        matches = self.fuzzy_match_transactions(bank_df, books_df)
        print(f"Final matches from fuzzy_match_transactions: {matches[:2] if isinstance(matches, list) else matches}")
        # Find unreconciled items
        unreconciled = self.find_unreconciled_items(bank_df, books_df, matches)

        return {
            "matches": matches,
            "unreconciled": unreconciled
        }