import streamlit as st
from question_generation import generate_questions

def render_sidebar():
    st.sidebar.header("About")
    st.sidebar.info(
        "ExamCraft AI is a smart tool that creates exam questions from your documents and descriptions. "
        "It uses Google's Gemini AI and Streamlit to work its magic. "
        "The app understands your needs and makes "
        "questions that fit your topic. Whether you're a teacher "
        "or just need to make quizzes, ExamCraft AI helps you save time and effort in creating great questions."
    )
    st.sidebar.header("Instructions")
    st.sidebar.markdown(
        """
        1. Upload one or more files (PDF, TXT, DOC, DOCX)
        2. Enter a description or context for the questions
        3. Specify the number of questions to generate
        4. Select the question type
        5. Click 'Generate Questions'
        6. View the generated questions and download if needed
        """
    )

def render_main_content(all_text):
    description = st.text_area(
        "Enter a description for your questions:",
        placeholder="Enter the description of your exam or mention the specific topics you want to practice",
        height=100
    )
    
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        num_questions = st.number_input("Number of questions", min_value=1, max_value=25, value=5)
    with col2:
        question_type = st.selectbox("Question type", ["MCQ", "Short Answer", "Multiple-response", "Long Answer", "True/False"])
    with col3:
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard", "Mix"])

    with col4:
        st.markdown("<style>.stButton > button { margin-top: 13px; }</style>", unsafe_allow_html=True)
        generate_button = st.button("Generate Questions")
    
    if generate_button:
        if not description:
            st.warning("Please enter a description before generating questions.")
        else:
            with st.spinner('Generating questions... This may take a few seconds.'):
                try:
                    questions_text = generate_questions(all_text, description, num_questions, question_type, difficulty)
                    
                    st.subheader(f"Generated {question_type} Questions:")
                    st.text_area("Questions", value=questions_text, height=400)
                    
                    st.download_button(
                        label="Download Questions",
                        data=questions_text,
                        file_name="generated_questions.txt",
                        mime="text/plain"
                    )
                except Exception as e:
                    st.error(f"An error occurred while generating questions: {str(e)}")