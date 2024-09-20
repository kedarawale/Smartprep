import re
import google.generativeai as genai
from text_processing import truncate_text

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