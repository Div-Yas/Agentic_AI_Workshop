from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from reconciliation import BankReconciliation
import os
from typing import Dict, List
import tempfile
from agents.reconciliation_knowledge_agent import ReconciliationKnowledgeAgent
import io

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize reconciliation engine
reconciliation_engine = BankReconciliation()
agent = ReconciliationKnowledgeAgent()

async def _process_files_and_call_reconciliation(bank_statement: UploadFile, books: UploadFile, reconciliation_func, *args_for_reconciliation_func):
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            bank_path = os.path.join(temp_dir, "bank_statement.csv")
            books_path = os.path.join(temp_dir, "books.csv")
            
            bank_content = await bank_statement.read()
            with open(bank_path, "wb") as f:
                f.write(bank_content)
            
            books_content = await books.read()
            with open(books_path, "wb") as f:
                f.write(books_content)
            
            if os.path.getsize(bank_path) == 0 or os.path.getsize(books_path) == 0:
                raise HTTPException(status_code=400, detail="One or both files are empty")
            
            bank_df, books_df = reconciliation_engine.load_data(bank_path, books_path)

            # If additional args are needed, they should be pre-calculated or passed through here.
            # For now, assuming basic calls or internal dependencies are handled within reconciliation_func
            return reconciliation_func(bank_df, books_df, *args_for_reconciliation_func)
            
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reconciliation/match")
async def match_reconciliation(
    bank_statement: UploadFile = File(...),
    books: UploadFile = File(...)
) -> Dict:
    """Process and return only matched transactions"""
    try:
        def _func(bank_df, books_df):
            matches = reconciliation_engine.process_match_reconciliation(bank_df, books_df)
            print(f"API endpoint matches: {matches}")  # Debug print
            return matches  # This should already be a dict with 'matches' key
        return await _process_files_and_call_reconciliation(bank_statement, books, _func)
    except Exception as e:
        print(f"Error in match_reconciliation: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/reconciliation/unmatched")
async def unmatched_reconciliation(
    bank_statement: UploadFile = File(...),
    books: UploadFile = File(...)
) -> Dict:
    """Process and return only unmatched transactions"""
    try:
        def _func(bank_df, books_df):
            matches = reconciliation_engine.process_match_reconciliation(bank_df, books_df)
            return reconciliation_engine.process_unmatched_reconciliation(bank_df, books_df, matches)
        return await _process_files_and_call_reconciliation(bank_statement, books, _func)
    except Exception as e:
        print(f"Error in unmatched_reconciliation: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/reconciliation/suggestions")
async def suggestions_for_fixes(
    bank_statement: UploadFile = File(...),
    books: UploadFile = File(...)
) -> Dict:
    """Process and return auto-fix suggestions for unreconciled items"""
    def _func(bank_df, books_df):
        matches = reconciliation_engine.process_match_reconciliation(bank_df, books_df)
        return {"auto_fixes": reconciliation_engine.process_suggestions_for_fixes(bank_df, books_df, matches)}
    return await _process_files_and_call_reconciliation(bank_statement, books, _func)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/ask-knowledge")
def ask_knowledge(question: str):
    try:
        answer = agent.query(question)
        return {"answer": answer}
    except Exception as e:
        return {"error": str(e)} 