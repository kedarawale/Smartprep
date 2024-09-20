import os
import io
from pypdf import PdfReader
from docx import Document

def extract_text_from_file(file):
    file_extension = os.path.splitext(file.name)[1].lower()
    try:
        if file_extension == '.pdf':
            pdf_reader = PdfReader(io.BytesIO(file.getvalue()))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            print(f"Extracted {len(text)} characters from PDF")
            return text
        elif file_extension == '.txt':
            return file.getvalue().decode('utf-8')
        elif file_extension in ['.doc', '.docx']:
            doc = Document(io.BytesIO(file.getvalue()))
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    except Exception as e:
        print(f"Error extracting text from {file.name}: {str(e)}")
        print(f"File content: {file.getvalue().decode('utf-8', errors='ignore')[:100]}...")
        return ""