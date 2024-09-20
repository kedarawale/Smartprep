import streamlit as st
import os
import google.generativeai as genai
from file_utils import extract_text_from_file
from question_generation import generate_questions
from ui_components import render_sidebar, render_main_content
from config import set_page_config

# Set page config as the first Streamlit command
set_page_config()

# Ensure you've set the GOOGLE_API_KEY environment variable
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Streamlit UI
st.title('ExamCraft AI')

st.write("""
This app generates questions and answers based on the content of uploaded files and user description.
Upload one or more files (PDF, TXT, DOC, DOCX), provide a description, specify the number of questions,
Select the difficulty level and select the question type you want to generate.
""")

uploaded_files = st.file_uploader("Upload files (PDF, TXT, DOC, DOCX)", type=['pdf', 'txt', 'doc', 'docx'], accept_multiple_files=True, key="file_uploader")

if uploaded_files:
    all_text = ""
    for file in uploaded_files:
        try:
            text = extract_text_from_file(file)
            if text.strip():
                all_text += text + "\n\n"
            else:
                st.warning(f"No text extracted from {file.name}. Skipping this file.")
        except Exception as e:
            st.error(f"Error processing file {file.name}: {str(e)}")

    if not all_text.strip():
        st.error("No valid text was extracted from the uploaded files. Please check your files and try again.")
    else:
        st.success("Files uploaded and processed successfully!")
        render_main_content(all_text)
else:
    st.info("Please upload one or more files to generate questions.")

render_sidebar()