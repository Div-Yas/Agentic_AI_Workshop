import streamlit as st
import requests
import pandas as pd
import json
from io import StringIO
import os
import re

st.set_page_config(page_title="Bank Reconciliation System", layout="wide")

# Initialize session state for processing flag
if 'processing_reconciliation' not in st.session_state:
    st.session_state.processing_reconciliation = False

st.markdown("""
    <style>
    /* Make file upload button blue */
    .stFileUploader > label div[data-testid="stFileUploaderDropzone"] {
        background-color: #1976d2 !important;
        color: white !important;
        border-radius: 8px;
        border: 2px solid #1976d2 !important;
    }
    .stFileUploader > label div[data-testid="stFileUploaderDropzone"]:hover {
        background-color: #1565c0 !important;
        color: white !important;
    }
    /* Make action buttons green */
    button[kind="primary"], .stButton > button {
        background-color: #43a047 !important;
        color: white !important;
        border-radius: 8px;
        border: 2px solid #43a047 !important;
    }
    button[kind="primary"]:hover, .stButton > button:hover {
        background-color: #388e3c !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Bank Reconciliation System")
st.write("Upload your bank statement and books records for automatic reconciliation")

# Sample files section
st.subheader("Sample Files")
col1, col2 = st.columns(2)

with col1:
    if st.button("Download Sample Bank Statement", disabled=st.session_state.processing_reconciliation):
        with open("../data/sample_bank_statement.csv", "r") as f:
            st.download_button(
                label="Click to Download Sample Bank Statement",
                data=f,
                file_name="sample_bank_statement.csv",
                mime="text/csv"
            )

with col2:
    if st.button("Download Sample Books Records", disabled=st.session_state.processing_reconciliation):
        with open("../data/sample_books.csv", "r") as f:
            st.download_button(
                label="Click to Download Sample Books Records",
                data=f,
                file_name="sample_books.csv",
                mime="text/csv"
            )

# File upload section
st.subheader("Upload Your Files")
col1, col2 = st.columns(2)

with col1:
    bank_statement = st.file_uploader("Upload Bank Statement (CSV)", type=['csv'], disabled=st.session_state.processing_reconciliation)
    if bank_statement:
        try:
            df_bank = pd.read_csv(bank_statement)
            st.write("Bank Statement Preview:")
            st.dataframe(df_bank, use_container_width=True, height=400)
            bank_statement.seek(0)
        except Exception as e:
            st.error(f"Error reading bank statement: {str(e)}")

with col2:
    books = st.file_uploader("Upload Books Records (CSV)", type=['csv'], disabled=st.session_state.processing_reconciliation)
    if books:
        try:
            df_books = pd.read_csv(books)
            st.write("Books Records Preview:")
            st.dataframe(df_books, use_container_width=True, height=400)
            books.seek(0)
        except Exception as e:
            st.error(f"Error reading books records: {str(e)}")

# Reconciliation Options and Processing
col_select, _ = st.columns([0.5, 1.5]) # Adjust width as needed
with col_select:
    reconciliation_option = st.selectbox(
        "Select Reconciliation Type:",
        ["Select an option", "Match Reconciliation", "Unmatched Reconciliation", "Suggestion For Fixes"],
        disabled=not (bank_statement and books)
    )

if reconciliation_option != "Select an option" and bank_statement and books:
    try:
        files = {
            'bank_statement': ('bank_statement.csv', bank_statement.getvalue(), 'text/csv'),
            'books': ('books.csv', books.getvalue(), 'text/csv')
        }
        
        endpoint = ""
        if reconciliation_option == "Match Reconciliation":
            endpoint = "/reconciliation/match"
        elif reconciliation_option == "Unmatched Reconciliation":
            endpoint = "/reconciliation/unmatched"
        elif reconciliation_option == "Suggestion For Fixes":
            endpoint = "/reconciliation/suggestions"

        if endpoint:
            st.session_state.processing_reconciliation = True  # Set flag to True
            with st.spinner(f'Processing {reconciliation_option}...'):
                response = requests.post(f"http://localhost:8000{endpoint}", files=files)
            print(f"Frontend received response: {response}")
            if response.status_code == 200:
                result = response.json()
                print(f"Frontend received response: {result}")  # Debug print
                
                # Display based on selected option
                if reconciliation_option == "Match Reconciliation":
                    matches_list = result.get('matches', [])
                    print(f"Frontend matches list: {matches_list}")  # Debug print
                    
                    if not matches_list:
                        st.write("No matched transactions found")
                    else:
                        st.subheader("Matched Transactions")
                        # Prepare data for DataFrame
                        df_matches = pd.DataFrame(matches_list)

                        # Filter for transactions where amount_match is True
                        if 'amount_match' in df_matches.columns:
                            df_matches = df_matches[df_matches['amount_match'] == True]
                            
                        # Convert boolean amount_match to '✅' or '❌'
                        if 'amount_match' in df_matches.columns:
                            df_matches['Amount Match'] = df_matches['amount_match'].apply(lambda x: '✅' if x else '❌')
                            df_matches = df_matches.drop(columns=['amount_match'])

                        # Rename columns for better display
                        df_matches = df_matches.rename(columns={
                            'bank_transaction_id': 'Bank ID',
                            'book_transaction_id': 'Book ID',
                            'description_match': 'Description Match',
                            'book_description': 'Book Description',
                            'bank_amount': 'Bank Amount',
                            'book_amount': 'Book Amount',
                            'confidence': 'Confidence'
                        })
                        
                        # Reorder columns for better presentation
                        display_columns = [
                            'Bank ID',
                            'Book ID',
                            'Description Match',
                            'Book Description',
                            'Bank Amount',
                            'Book Amount',
                            'Amount Match',
                            'Confidence'
                        ]
                        
                        # Ensure only existing columns are used
                        df_matches = df_matches[[col for col in display_columns if col in df_matches.columns]]
                        
                        st.dataframe(df_matches, use_container_width=True, hide_index=True)

                elif reconciliation_option == "Unmatched Reconciliation":
                    unreconciled_items = result.get('unreconciled', [])
                    if unreconciled_items:
                        st.subheader("Unreconciled Items")
                        
                        # Prepare data for DataFrame
                        df_unreconciled = pd.DataFrame(unreconciled_items)

                        # Rename columns for better display
                        df_unreconciled = df_unreconciled.rename(columns={
                            'bank_transaction_id': 'Bank ID',
                            'book_transaction_id': 'Book ID',
                            'description': 'Description',
                            'bank_amount': 'Bank Amount',
                            'book_amount': 'Book Amount',
                            'reason': 'Reason/Discrepancy',
                            'type': 'Type'
                        })
                        
                        # Reorder columns for better presentation
                        display_columns = [
                            'Bank ID',
                            'Book ID',
                            'Description',
                            'Bank Amount',
                            'Book Amount',
                            'Type',
                            'Reason/Discrepancy'
                        ]
                        
                        # Ensure only existing columns are used
                        df_unreconciled = df_unreconciled[[col for col in display_columns if col in df_unreconciled.columns]]
                        
                        st.dataframe(df_unreconciled, use_container_width=True, hide_index=True)
                    else:
                        st.write("No unreconciled items found")

                elif reconciliation_option == "Suggestion For Fixes":
                    auto_fixes = result.get('auto_fixes', [])
                    if auto_fixes:
                        st.subheader("Auto-Fix Suggestions")
                        
                        # Prepare data for DataFrame
                        suggestions_data = []
                        for fix in auto_fixes:
                            suggestions_data.append({
                                'Discrepancy Type': fix.get('discrepancy', {}).get('type', 'N/A'),
                                'Bank ID': fix.get('discrepancy', {}).get('bank_transaction_id', 'N/A'),
                                'Book ID': fix.get('discrepancy', {}).get('book_transaction_id', 'N/A'),
                                'Suggestion': fix.get('suggestion', 'N/A')
                            })
                        
                        df_suggestions = pd.DataFrame(suggestions_data)
                        
                        st.dataframe(df_suggestions, use_container_width=True, hide_index=True)
                    else:
                        st.write("No auto-fix suggestions found")
            else:
                st.error(f"Error processing files: {response.text}")
        else:
            st.warning("Please select a reconciliation type.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
    finally:
        st.session_state.processing_reconciliation = False # Reset flag to False

# Instructions
with st.expander("How to use"):
    st.write("""
    1. Download the sample files to understand the required format
    2. Prepare your bank statement and books records in CSV format
    3. Upload both files using the file uploaders above
    4. Select a reconciliation type from the dropdown to start the process
    5. Review the results in the sections below
    """) 