from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from typing import Dict
from config import GOOGLE_API_KEY
import json
import re

class AutoFixSuggestionAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=GOOGLE_API_KEY,
            temperature=0.7
        )

    def suggest_fixes(self, discrepancy: Dict) -> Dict:
        """Suggests fixes for a given discrepancy using LLM"""
        prompt = PromptTemplate(
            input_variables=["discrepancy"],
            template="""
            Analyze the following bank reconciliation discrepancy and suggest a precise fix or a detailed next action. 
            Focus on practical accounting or investigation steps. If a journal entry is suggested, include the debits and credits.
            
            Discrepancy: {discrepancy}
            
            Return the suggestion in JSON format, with a key 'suggestion' containing the text. Example:
            {{
                "suggestion": "Investigate missing invoice, then make a journal entry: Debit Accounts Receivable, Credit Service Revenue."
            }}
            """
        )
        llm_response = self.llm.invoke(
            prompt.format(
                discrepancy=str(discrepancy)
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
            print(f"No valid JSON object or array found in LLM response for Auto-Fix Suggestion: {json_string}")
            return {"suggestion": "Could not generate a specific fix."}

        try:
            parsed_json = json.loads(json_string)
            return parsed_json.get("suggestion", "Could not parse suggestion.")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON for Auto-Fix Suggestion from LLM: {e}")
            print(f"Problematic JSON string for Auto-Fix Suggestion: {json_string}")
            return {"suggestion": "Could not generate a specific fix due to parsing error."} 