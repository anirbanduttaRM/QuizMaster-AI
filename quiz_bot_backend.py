import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

# Load environment variables from the .env file
load_dotenv()

class QuizBotBackend:
    def __init__(self, api_key):
        """Initialize the QuizBotBackend with the Gemini API key."""
        self.api_key = api_key
        genai.configure(api_key=self.api_key)  # Configure Gemini API
        self.model = genai.GenerativeModel("models/gemini-1.5-flash")  # Specify the model

    def get_quiz_questions(self, standard):
        """
        Fetch quiz questions for the selected standard, ensuring questions are of appropriate complexity.

        Args:
            standard (str): The selected standard (e.g., "Standard 1").

        Returns:
            list: A list of quiz questions in JSON format.
        """
        prompt = self.generate_prompt(standard)
        
        try:
            # Generate content using the Gemini API
            result = self.model.generate_content(prompt)
            raw_response = result.text
            print(f"Raw API response: {raw_response}")  # Debugging: log the raw response
        except Exception as e:
            print(f"Error generating content: {e}")
            return []

        # Parse and format the result into structured quiz data
        quiz_data = self.parse_quiz_data(raw_response)
        return quiz_data

    def generate_prompt(self, standard):
        """
        Generate the prompt dynamically based on the selected standard.

        Args:
            standard (str): The selected standard (e.g., "Standard 1").

        Returns:
            str: A formatted prompt for the Gemini API.
        """
        prompt = (
            f"Create 10 MCQs for CBSE class {standard} students based on the NCERT syllabus. "
            "Questions should cover all sbjects, age-appropriate, and not too simple. "
            "Each question must have four options prefixed with 'a)', 'b)', 'c)', 'd)', and one correct answer. "
            "Output a valid JSON array in this format:\n"
            "[\n"
            "    {\n"
            "        \"question\": \"Which of these is a festival celebrated in India?\",\n"
            "        \"options\": [\"a) Christmas\", \"b) Diwali\", \"c) Halloween\", \"d) Thanksgiving\"],\n"
            "        \"correct_answer\": \"b) Diwali\"\n"
            "    }\n"
            "]\n"
            "At the end, append an answer key like:\n"
            "Answer Key:\n"
            "1: b)\n"
            "2: c)\n"
            "3: d)\n"
        )
        return prompt

    def parse_quiz_data(self, result_text):
        """
        Parse the API response into structured quiz data.

        Args:
            result_text (str): The raw response text from the Gemini API.

        Returns:
            list: A list of quiz questions in JSON format.
        """
        try:
            # Extract the JSON block from the raw response
            start_index = result_text.find("```json")
            end_index = result_text.find("```", start_index + len("```json"))
            
            if start_index == -1 or end_index == -1:
                print("Error: JSON block not found in the response.")
                return []

            json_block = result_text[start_index + len("```json"):end_index].strip()
            quiz_data = json.loads(json_block)

            # Extract and assign correct answers from the answer key
            self.add_correct_answers(quiz_data, result_text)
            return quiz_data
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error parsing quiz data: {e}")
            return []

    def add_correct_answers(self, quiz_data, result_text):
        """
        Extract answers from the answer key and assign them to the questions.

        Args:
            quiz_data (list): The list of quiz questions.
            result_text (str): The raw response text from the Gemini API.
        """
        try:
            # Extract the answer key section from the response
            answer_key_section = result_text.split("Answer Key:")[-1].strip()
            
            # Split the answer key into lines and filter out empty ones
            answers = [line.strip() for line in answer_key_section.split("\n") if line.strip()]
            
            # Map answers to quiz data
            for idx, answer_line in enumerate(answers):
                if idx < len(quiz_data):
                    # Safely split the answer line
                    parts = answer_line.split(":")
                    if len(parts) > 1:
                        correct_option_label = parts[1].strip()  # e.g., "b)"
                        
                        # Find the corresponding option text
                        options = quiz_data[idx]["options"]
                        for option in options:
                            if option.startswith(correct_option_label):
                                quiz_data[idx]["correct_answer"] = option  # e.g., "b) Mango"
                                break
                    else:
                        print(f"Skipping malformed answer line: {answer_line}")
        except Exception as e:
            print(f"Error parsing answer key: {e}")


# Example usage:
# api_key = os.getenv("GEMINI_API_KEY")
# quiz_bot_backend = QuizBotBackend(api_key)
# quiz_data = quiz_bot_backend.get_quiz_questions("Standard 1")
# print(quiz_data)