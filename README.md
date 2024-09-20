

# ExamCraft AI

ExamCraft AI is an intelligent tool that automatically generates exam questions from uploaded documents and user descriptions. It leverages Google's Gemini AI and Streamlit to create customized questions for various educational purposes.

## Features

- Upload multiple file types (PDF, TXT, DOC, DOCX)
- Extract text from uploaded documents
- Generate questions based on document content and user description
- Customize question generation:
  - Number of questions (1-25)
  - Question types (MCQ, Short Answer, Multiple-response, Long Answer, True/False)
  - Difficulty levels (Easy, Medium, Hard, Mix)
- Download generated questions as a text file
- User-friendly web interface

## Installation

1. Clone the repository:
```bash
   git clone https://github.com/yourusername/ExamCraft-AI.git
   cd ExamCraft-AI
   ```

2. Install the required dependencies:
  ```bash 
  pip install -r requirements.txt
  ```
3. Set up your Google API key:
```bash
   Set the environment variable:
   export GOOGLE_API_KEY=your_api_key_here
```

## Usage

1. Run the Streamlit app:
   streamlit run app.py

2. Open your web browser and navigate to the provided local URL (usually http://localhost:8501)

3. Follow the on-screen instructions:
   - Upload one or more files (PDF, TXT, DOC, DOCX)
   - Enter a description or context for the questions
   - Specify the number of questions to generate
   - Select the question type and difficulty level
   - Click 'Generate Questions'
   - View the generated questions and download if needed

## Dependencies

- streamlit
- pypdf
- python-docx
- sentence-transformers
- google-generativeai
- tiktoken

## How It Works

1. The app extracts text from uploaded documents using libraries like pypdf and python-docx.
2. It uses the Sentence Transformer model for text embeddings.
3. The extracted text and user description are sent to Google's Gemini Pro AI model to generate questions.
4. The generated questions are parsed, validated, and formatted according to the specified question type.
5. The results are displayed in the Streamlit interface and can be downloaded as a text file.

## Contributing

Contributions to ExamCraft AI are welcome! Please feel free to submit pull requests, create issues or spread the word.

## License

[MIT License](LICENSE)



