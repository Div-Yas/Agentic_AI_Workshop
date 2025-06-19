import streamlit as st
import requests

st.set_page_config(page_title="Knowledge Agent", layout="wide")

st.title("Ask the Knowledge Agent")

# Add some styling
st.markdown("""
    <style>
    .stTextInput > div > div > input {
        background-color: #f0f2f6;
        border-radius: 8px;
        padding: 10px;
    }
    .stButton > button {
        background-color: #43a047;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        border: none;
    }
    .stButton > button:hover {
        background-color: #388e3c;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Create a text input for the question
question = st.text_input("Ask a question about bank reconciliation:")

# Create a button to submit the question
if st.button("Ask"):
    if question:
        with st.spinner("Processing your question..."):
            try:
                # Make request to the backend
                response = requests.get(f"http://localhost:8000/ask-knowledge?question={question}")
                if response.status_code == 200:
                    answer = response.json().get("answer", "No answer found.")
                    st.markdown("### Answer:")
                    st.write(answer)
                else:
                    st.error("Failed to get an answer. Please try again.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please enter a question first.")