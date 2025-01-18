import tkinter as tk
from tkinter import messagebox


class QuizBotFrontend:
    def __init__(self, bot_backend):
        self.backend = bot_backend
        self.window = tk.Tk()
        self.window.title("TechBot Quiz")

        # Set initial values
        self.selected_standard = None
        self.quiz_data = []
        self.current_question_index = 0
        self.score = 0

        # Create components for selecting standard
        self.standard_label = tk.Label(self.window, text="Select Standard:")
        self.standard_label.pack()

        self.standard_select = tk.StringVar(value="Standard 1")
        self.standard_menu = tk.OptionMenu(self.window, self.standard_select, *[f"Standard {i}" for i in range(1, 11)])
        self.standard_menu.pack()

        self.start_button = tk.Button(self.window, text="Start Quiz", command=self.start_quiz)
        self.start_button.pack()

        # Create a frame for displaying quiz questions
        self.quiz_frame = tk.Frame(self.window)

        self.question_label = tk.Label(self.quiz_frame, text="Question will appear here")
        self.question_label.pack()

        self.options_var = tk.StringVar()
        self.options_buttons = []

        self.submit_button = tk.Button(self.quiz_frame, text="Next", command=self.next_question)
        self.submit_button.pack()

    def start_quiz(self):
        """Start the quiz by fetching questions from backend."""
        self.selected_standard = self.standard_select.get()
        print(f"Selected standard: {self.selected_standard}")  # Debugging: log selected standard
        
        # Fetch the quiz data from the backend
        self.quiz_data = self.backend.get_quiz_questions(self.selected_standard)
        print(f"Fetched quiz data: {self.quiz_data}")  # Debugging: log quiz data

        # Check if quiz data is valid
        if not self.quiz_data:
            print("Error: No valid quiz data fetched.")  # Debugging: log error
            messagebox.showerror("Error", "Failed to fetch valid quiz questions.")
            return

        # Initialize quiz variables
        self.current_question_index = 0
        self.score = 0

        # Hide the standard selection UI
        self.standard_label.pack_forget()
        self.standard_menu.pack_forget()
        self.start_button.pack_forget()

        # Show the quiz frame
        self.quiz_frame.pack()
        print("Quiz started!")  # Debugging: log quiz start

        # Show the first question
        self.show_question()

    def show_question(self):
        """Display the current question and its options."""
        if self.current_question_index >= len(self.quiz_data):
            self.end_quiz()
            return

        # Fetch the current question data
        question_data = self.quiz_data[self.current_question_index]

        # Update question label with the new question
        self.question_label.config(text=f"Q{self.current_question_index + 1}: {question_data['question']}")

        # Clear previous options and reset variable
        self.options_var.set(None)
        for button in self.options_buttons:
            button.destroy()
        self.options_buttons.clear()

        # Create new options for the current question
        for opt in question_data["options"]:
            button = tk.Radiobutton(
                self.quiz_frame, text=opt, value=opt, variable=self.options_var, anchor="w", wraplength=400
            )
            button.pack(anchor='w')
            self.options_buttons.append(button)


    def next_question(self):
        """Handle the next question and check the answer."""
        selected_option = self.options_var.get()

        if not selected_option:
            messagebox.showwarning("No answer selected", "Please select an option before proceeding.")
            return

        # Check the correctness of the answer
        correct_answer = self.quiz_data[self.current_question_index]["correct_answer"]
        if selected_option == correct_answer:
            self.score += 1
            messagebox.showinfo("Correct!", "Great job! You got the answer right.")
        else:
            messagebox.showerror("Incorrect!", f"The correct answer was: {correct_answer}")

        # Move to the next question
        self.current_question_index += 1
        self.show_question()  # Show the next question

    def end_quiz(self):
        """End the quiz and show the score."""
        print(f"Quiz completed. Final score: {self.score}/{len(self.quiz_data)}")  # Debugging: log final score
        messagebox.showinfo("Quiz Completed", f"Your score is: {self.score}/{len(self.quiz_data)}")
        self.window.quit()  # Close the window after quiz completion