import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

# Load environment variables from the .env file
load_dotenv()

class QuizBotBackend:
    def __init__(self, api_key):
        self.api_key = api_key
        genai.configure(api_key=self.api_key)  # Configure Gemini API
        self.model = genai.GenerativeModel("models/gemini-1.5-flash")  # Specify the model

    def get_quiz_questions(self, standard):
        """Fetch quiz questions for the selected standard, ensuring questions are of appropriate complexity."""
        prompt = self.generate_prompt(standard)
        
        # Try generating content with proper error handling
        try:
            result = self.model.generate_content(prompt)
            raw_response = result.text
        except Exception as e:
            print(f"Error generating content: {e}")
            return []
        
        # Parse and format the result into structured quiz data
        quiz_data = self.parse_quiz_data(raw_response)
        return quiz_data

    def generate_prompt(self, standard):
        """Generate the prompt dynamically based on the selected standard."""
        prompt = (
                    f"Create a quiz for CBSE class {standard} students with 10 MCQs. "
                    "Questions should be age-appropriate and aligned with the NCERT syllabus. "
                    "Avoid overly simple questions and cover all subjects. "
                    "Provide the output as a valid JSON array with this structure:\n"
                    "[\n"
                    "    {\n"
                    "        \"question\": \"Which of these is a festival celebrated in India?\",\n"
                    "        \"options\": [\"Christmas\", \"Diwali\", \"Halloween\", \"Thanksgiving\"],\n"
                    "        \"correct_answer\": \"Diwali\"\n"
                    "    }\n"
                    "]\n"
                    "Each question must have exactly four options, and one correct answer. "
                    "Append the answer key in this format:\n"
                    "Answer Key:\n"
                    "1: b)\n"
                    "2: c)\n"
                    "3: d)\n"
                    )
        return prompt

    def parse_quiz_data(self, result_text):
        """Parse the API response into structured quiz data."""
        print(f"Raw API response: {result_text}")  # Debugging: log the raw response
        
        try:
            # Extract only the JSON block from the raw response
            start_index = result_text.find("```json")
            end_index = result_text.find("```", start_index + len("```json"))
            
            if start_index != -1 and end_index != -1:
                json_block = result_text[start_index + len("```json"):end_index].strip()
                # Parse the extracted JSON block
                quiz_data = json.loads(json_block)
                return quiz_data
            else:
                print("Error: JSON block not found in the response.")
                return []
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return []
    
    def add_correct_answers(self, quiz_data, result_text):
        """Extract answers from the answer key and assign them to the questions."""
        try:
            answer_key_section = result_text.split("Answer Key:")[-1].strip()
            answers = answer_key_section.split("\n")
            
            for idx, answer_line in enumerate(answers):
                if idx < len(quiz_data):
                    # Extract the answer option (e.g., "1: d)") and map it to the correct answer
                    correct_option = answer_line.split(":")[1].strip()
                    # Update the "correct_answer" with the correct option label
                    quiz_data[idx]["correct_answer"] = correct_option
        except Exception as e:
            print(f"Error parsing answer key: {e}")
