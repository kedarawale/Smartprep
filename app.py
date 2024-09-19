import streamlit as st
import os
import io
from PyMuPDF import fitz
import docx2txt
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
import tiktoken
import warnings
import re
warnings.filterwarnings("ignore", category=FutureWarning)

# Set page config as the first Streamlit command
st.set_page_config(page_title="ExamCraft AI", layout="wide")


# Ensure you've set the GOOGLE_API_KEY environment variable
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

def extract_text_from_file(file):
    file_extension = os.path.splitext(file.name)[1].lower()
    try:
        if file_extension == '.pdf':
            with fitz.open(stream=file.read(), filetype="pdf") as pdf:
                text = ""
                for page in pdf:
                    text += page.get_text()
                return text
        elif file_extension == '.txt':
            return file.getvalue().decode('utf-8')
        elif file_extension in ['.doc', '.docx']:
            return docx2txt.process(io.BytesIO(file.getvalue()))
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    except Exception as e:
        print(f"Error extracting text from {file.name}: {str(e)}")
        return ""

def num_tokens_from_string(string: str, encoding_name: str = "cl100k_base") -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def truncate_text(text: str, max_tokens: int = 3000) -> str:
    tokens = tiktoken.get_encoding("cl100k_base").encode(text)
    if len(tokens) <= max_tokens:
        return text
    return tiktoken.get_encoding("cl100k_base").decode(tokens[:max_tokens])

def generate_questions(text, description, num_questions, question_type, difficulty, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            truncated_text = truncate_text(text, 3000)
            
            prompt = f"""
            Based on the following text and description, generate exactly {num_questions} {question_type} questions.
            
            Text: {truncated_text}
            
            Description: {description}

            Question Type: {question_type}
            Difficulty: {difficulty}

            Format the questions strictly as follows:

            For MCQ:
            Q1: [Question text]
            A) [Option A]
            B) [Option B]
            C) [Option C]
            D) [Option D]
            Correct Answer: [Correct option letter]

            For Short Answer:
            Q1: [Question text]
            A: [Brief answer]
            
            For Two Answer MCQ:
            Q1: [Question text]
            A) [Option A]
            B) [Option B]
            C) [Option C]
            D) [Option D]
            Correct Answer: [Two correct option letters, e.g., A, C]
            
            For Multiple-response:
            Q1: [Question text]
            A) [Option A]
            B) [Option B]
            C) [Option C]
            D) [Option D]
            Correct Answer: [Correct option letters, e.g., A, C, D]
            
            For Long Answer:
            Q1: [Question text]
            A: [Detailed answer or key points to be included in the answer]

            For True/False:
            Q1: [Question text]
            A: True
            or
            Q1: [Question text]
            A: False
            
            
            For Multiple-response:
            Q1: [Question text]
            A) [Option A]
            B) [Option B]
            C) [Option C]
            D) [Option D]
            Correct Answer: [Correct option letters, e.g., A, C, D]
            
            For Long Answer:
            Q1: [Question text]
            A: [Detailed answer or key points to be included in the answer]

            Important instructions:
            1. Generate exactly {num_questions} questions.
            2. Strictly follow the format provided for each question type.
            3. Ensure each question is complete and properly formatted before moving to the next.
            4. Include question numbers (Q1, Q2, Q3, etc.) for each question.
            5. Make sure the questions are diverse and cover different aspects of the text.
            6. Align the questions with the given description and difficulty level.
            7. Use 'Q1:', 'Q2:', etc. for questions and 'A:' for answers consistently.
            8. For 'Mix' difficulty, provide a balanced set of easy, medium, and hard questions.
            9. Do not include any explanations or additional text outside the specified format.
            10. For True/False questions, the answer must be exactly 'True' or 'False'.

            Begin generating the questions now:
            """

            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            
            parsed_questions = parse_output(response.text, question_type)
            formatted_questions = '\n\n'.join(parsed_questions)

            is_valid, valid_questions = validate_questions(formatted_questions, question_type, num_questions)
            if is_valid:
                return valid_questions
            else:
                print(f"Attempt {attempt + 1}: Generated questions did not meet the required format. Retrying...")

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")

    raise Exception("Failed to generate valid questions after maximum attempts")

def parse_output(output, question_type):
    questions = []
    current_question = []
    
    for line in output.split('\n'):
        line = line.strip()
        if re.match(r'Q\d+:', line):
            if current_question:
                questions.append('\n'.join(current_question))
                current_question = []
            current_question.append(line)
        elif line:
            current_question.append(line)

    if current_question:
        questions.append('\n'.join(current_question))

    # Ensure consistent formatting
    formatted_questions = []
    for question in questions:
        lines = question.split('\n')
        formatted_question = []
        options = []
        answer_lines = []
        in_answer = False
        
        for line in lines:
            if re.match(r'Q\d+:', line):
                formatted_question.append(line)
            elif line.startswith('A:'):
                in_answer = True
                answer_lines.append(line)
            elif in_answer and question_type == "Long Answer":
                answer_lines.append(line)
            elif re.match(r'^[A-D]\)', line) or re.match(r'^[A-D]\.', line):
                options.append(line)
            elif line.lower().startswith("correct answer:"):
                answer_lines.append(line)
        
        if question_type in ["MCQ", "Multiple-response"]:
            formatted_question.extend(options)
            if answer_lines:
                formatted_question.append(answer_lines[0])
        elif question_type == "Long Answer":
            formatted_question.extend(answer_lines)
        else:  # Short Answer and True/False
            if answer_lines:
                formatted_question.append(answer_lines[0])
        
        formatted_questions.append('\n'.join(formatted_question))

    return formatted_questions

def validate_questions(questions, question_type, num_questions):
    valid_questions = []
    for question in questions.split('\n\n'):
        lines = question.split('\n')
        if question_type == "MCQ":
            if len(lines) == 6 and lines[0].startswith('Q') and all(l.startswith(opt) for l, opt in zip(lines[1:5], 'ABCD')) and lines[5].startswith('Correct Answer:'):
                valid_questions.append(question)
        elif question_type == "Short Answer":
            if len(lines) == 2 and lines[0].startswith('Q') and lines[1].startswith('A:'):
                valid_questions.append(question)
        elif question_type in ["Two Answer MCQ", "Multiple-response"]:
            if len(lines) == 6 and lines[0].startswith('Q') and all(l.startswith(opt) for l, opt in zip(lines[1:5], 'ABCD')) and lines[5].startswith('Correct Answer:'):
                valid_questions.append(question)
        elif question_type == "Long Answer":
            if len(lines) >= 2 and lines[0].startswith('Q') and lines[1].startswith('A:'):
                valid_questions.append(question)
        elif question_type == "True/False":
            if len(lines) == 2 and lines[0].startswith('Q') and lines[1].startswith('A:') and lines[1].lower() in ['a: true', 'a: false']:
                valid_questions.append(question)
    
    return len(valid_questions) == num_questions, '\n\n'.join(valid_questions)


# Initialize SentenceTransformer for embeddings
@st.cache_resource
def load_embedding_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

embedding_model = load_embedding_model()

# Streamlit UI
st.title('ExamCraft AI')

st.write("""
This app generates questions and answers based on the content of uploaded files and user description.
Upload one or more files (PDF, TXT, DOC, DOCX), provide a description, specify the number of questions,
Select the difficulty level and select the question type you want to generate.
""")

uploaded_files = st.file_uploader("Upload files (PDF, TXT, DOC, DOCX)", type=['pdf', 'txt', 'doc', 'docx'], accept_multiple_files=True)

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
                        
                        st.subheader(f"Generated {question_type} Questions")
                        st.text(questions_text)  # Use st.text to preserve formatting
                        
                        
                        # Option to download questions as a text file
                        st.download_button(
                            label="Download Questions",
                            data=questions_text,
                            file_name=f"{question_type.lower().replace(' ', '_')}_{difficulty.lower()}_questions.txt",
                            mime="text/plain"
                        )
                    except Exception as e:
                        st.error(f"Error generating questions: {str(e)}")
                        st.error("Please try again or adjust your inputs.")
else:
    st.info("Please upload one or more files to generate questions.")

# Add some information about the app
st.sidebar.header("About")
st.sidebar.info(
    "ExamCraft AI is a smart tool that creates exam questions from your documents and descriptions. "
    "It uses Google's Gemini AI and Streamlit to work its magic. "
    "The app understands your needs and makes "
    "questions that fit your topic.Whether you're a teacher "
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
