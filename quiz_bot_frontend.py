import tkinter as tk
from tkinter import messagebox, ttk
#from playsound import playsound
import threading  # To avoid blocking the UI with sound playback
from PIL import Image, ImageTk
import re
import pygame
import sys

class QuizBotFrontend:
    def __init__(self, bot_backend):
        self.backend = bot_backend
        self.window = tk.Tk()
        self.window.title("TechBot Quiz")
        self.window.geometry("600x400")  # Set a fixed window size
        self.window.configure(bg="#f4f4f4")  # Light background color

        # Set initial values
        self.selected_standard = None
        self.quiz_data = []
        self.current_question_index = 0
        self.score = 0
        self.timer = None
        self.time_remaining = 20  # Timer starts with 20 seconds for each question

        # Title Label
        self.title_label = tk.Label(
            self.window,
            text="Welcome to TechBot Quiz!",
            font=("Helvetica", 18, "bold"),
            bg="#f4f4f4",
            fg="#333"
        )
        self.title_label.pack(pady=20)

        # Create components for selecting standard
        self.standard_frame = tk.Frame(self.window, bg="#f4f4f4")
        self.standard_frame.pack()

        self.standard_label = tk.Label(
            self.standard_frame,
            text="Select Standard:",
            font=("Helvetica", 14),
            bg="#f4f4f4",
            fg="#333"
        )
        self.standard_label.grid(row=0, column=0, padx=10, pady=10)

        self.standard_select = tk.StringVar(value="Standard 1")
        self.standard_menu = tk.OptionMenu(
            self.standard_frame,
            self.standard_select,
            *[f"Standard {i}" for i in range(1, 11)]
        )
        self.standard_menu.config(font=("Helvetica", 12), bg="#e0e0e0", fg="#333")
        self.standard_menu.grid(row=0, column=1, padx=10, pady=10)

        self.start_button = tk.Button(
            self.window,
            text="Start Quiz",
            font=("Helvetica", 14, "bold"),
            bg="#4caf50",
            fg="#fff",
            activebackground="#388e3c",
            activeforeground="#fff",
            command=self.start_quiz
        )
        self.start_button.pack(pady=20)

        # Create a frame for displaying quiz questions
        self.quiz_frame = tk.Frame(self.window, bg="#f4f4f4")

        self.question_label = tk.Label(
            self.quiz_frame,
            text="Question will appear here",
            font=("Helvetica", 16, "bold"),
            wraplength=500,
            bg="#f4f4f4",
            fg="#333",
            justify="center"
        )
        self.question_label.pack(pady=20)

        self.options_var = tk.StringVar()
        self.options_buttons = []

        self.timer_label = tk.Label(
            self.quiz_frame,
            text="Time remaining: 20 seconds",
            font=("Helvetica", 12, "bold"),
            bg="#f4f4f4",
            fg="#d32f2f"
        )
        self.timer_label.pack(pady=10)

        self.submit_button = tk.Button(
            self.quiz_frame,
            text="Next",
            font=("Helvetica", 14, "bold"),
            bg="#2196f3",
            fg="#fff",
            activebackground="#1976d2",
            activeforeground="#fff",
            command=self.next_question
        )
        self.submit_button.pack(pady=20)

        # Frame for options
        self.options_frame = tk.Frame(self.quiz_frame, bg="#f4f4f4")
        self.options_frame.pack()

        # Initialize pygame mixer here to ensure it's done before playing any sound
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)

    def play_sound(self, sound_path):
        """Play sound using pygame."""
        # Load and play the sound file asynchronously
        sound = pygame.mixer.Sound(sound_path)
        sound.play()

    def start_quiz(self):
        """Start the quiz by fetching questions from backend."""
        self.selected_standard = self.standard_select.get()
        self.quiz_data = self.backend.get_quiz_questions(self.selected_standard)

        if not self.quiz_data:
            messagebox.showerror("Error", "Failed to fetch valid quiz questions.")
            return

        # Initialize quiz variables
        self.current_question_index = 0
        self.score = 0

        # Hide the standard selection UI
        self.standard_frame.pack_forget()
        self.start_button.pack_forget()

        # Show the quiz frame
        self.quiz_frame.pack()

        # Show the first question
        self.show_question()

    def show_question(self):
        """Display the current question and its options."""
        if self.current_question_index >= len(self.quiz_data):
            self.end_quiz()
            return

        # Reset timer for each question
        self.time_remaining = 20  # Reset to 20 seconds
        self.update_timer()

        question_data = self.quiz_data[self.current_question_index]
        self.question_label.config(
            text=f"Q{self.current_question_index + 1}: {question_data['question']}",
            font=("Helvetica", 16, "bold"),
            wraplength=500,
            justify="center"
        )

        # Clear the options frame
        for widget in self.options_frame.winfo_children():
            widget.destroy()

        # Reset the variable for options
        self.options_var.set("")  # Ensures no radio button is preselected

        # Ensure there are 4 options
        options = question_data["options"]
        while len(options) < 4:
            options.append("")  # Pad with empty strings

        # Define custom styles for Radiobuttons
        style = ttk.Style()
        style.configure(
            "Custom.TRadiobutton",
            font=("Helvetica", 14),
            background="#f4f4f4",  # Light background for radiobutton area
            foreground="#333",     # Dark text color for readability
            padding=(10, 5),       # Add padding inside the buttons
        )
        style.map(
            "Custom.TRadiobutton",
            background=[("active", "#e0f7fa")],  # Highlighted background on hover
            foreground=[("active", "#00796b")],  # Highlighted text color on hover
        )

        # Create new options as Radiobuttons in a single row
        for col, opt in enumerate(options):
            button = ttk.Radiobutton(
                self.options_frame,
                text=opt if opt else "No option provided",  # Handle empty options gracefully
                value=opt,
                variable=self.options_var,
                style="Custom.TRadiobutton",
                cursor="hand2"  # Change cursor to hand when hovering
            )
            button.grid(row=0, column=col, padx=15, pady=5, sticky="w")  # Arrange in a single row

    def update_timer(self):
        """Update the timer for the current question."""
        if self.time_remaining > 0:
            self.timer_label.config(text=f"Time remaining: {self.time_remaining} seconds")
            self.time_remaining -= 1
            self.timer = self.window.after(1000, self.update_timer)
        else:
            # Show the correct answer when time is up
            question_data = self.quiz_data[self.current_question_index]
            correct_answer = question_data["correct_answer"]
            self.show_time_up_message(correct_answer)


    def custom_message_box(self, title, message, image_path=None, sound_path=None, callback=None, close_after=3):
        """
        Display a custom message box that disappears after a specified number of seconds
        and optionally calls a callback.

        Args:
            title (str): Title of the message box.
            message (str): Message to display.
            image_path (str, optional): Path to an image to display. Defaults to None.
            sound_path (str, optional): Path to a sound file to play. Defaults to None.
            callback (callable, optional): Function to call after the popup closes. Defaults to None.
            close_after (int, optional): Number of seconds before closing the popup. Defaults to 3.
        """
        # Optionally play a sound
        def play_sound_thread():
            if sound_path:
                self.play_sound(sound_path)

        threading.Thread(target=play_sound_thread).start()

        # Create a new popup window
        popup = tk.Toplevel(self.window)
        popup.title(title)
        popup.geometry("300x150")  # Default smaller size
        popup.configure(bg="#f4f4f4")

        # Add an optional image to the popup
        if image_path:
            img = Image.open(image_path)
            img = img.resize((60, 60), Image.Resampling.LANCZOS)  # Smaller image
            img_tk = ImageTk.PhotoImage(img)

            img_label = tk.Label(popup, image=img_tk, bg="#f4f4f4")
            img_label.image = img_tk
            img_label.pack(pady=5)

        # Add the message with wrapping
        msg_label = tk.Label(
            popup,
            text=message,
            font=("Helvetica", 12),
            bg="#f4f4f4",
            fg="#333",
            wraplength=280,  # Wrap text at 280 pixels (adjustable based on popup size)
            justify="center"  # Center-align the text
        )
        msg_label.pack(pady=5, fill="both", expand=True)

        # Automatically close the popup after the specified time and execute callback if provided
        def close_popup():
            if popup.winfo_exists():  # Ensure the popup still exists before trying to destroy it
                popup.destroy()
                if callback:
                    callback()

        # Schedule the popup to close after the specified time
        popup.after(close_after * 1000, close_popup)  # Convert seconds to milliseconds

    def next_question(self, skip_message_box=False):
        """Handle the next question and check the answer."""
        # Cancel the current timer if it's running
        if self.timer:
            self.window.after_cancel(self.timer)

        # Centralized quiz completion check **before accessing quiz_data**
        if self.current_question_index >= len(self.quiz_data):
            print(f"Debug: No more questions! Index: {self.current_question_index}, Total: {len(self.quiz_data)}")
            self.window.after(5000, self.end_quiz)  # Pause for 5 seconds before ending
            return  # Prevent further execution

        # Skip showing a custom message box if the flag is set
        if skip_message_box:
            self.current_question_index += 1
        else:
            # Get the selected option
            selected_option = self.options_var.get()

            # Clean up both selected option and correct answer (removes prefixes and extra spaces)
            def clean_option(option):
                """Remove any prefixes (like 'a)', 'b)') and extra spaces."""
                if option and isinstance(option, str):  # Ensure the option is a non-empty string
                    return re.sub(r'^[a-d]\)\s*', '', option).strip().lower()
                return option.strip().lower()  # Fallback to just stripping and lowering

            # **Ensure index is valid before accessing quiz_data**
            if self.current_question_index >= len(self.quiz_data):
                print(f"Error: Attempted to access question index {self.current_question_index}, but only {len(self.quiz_data)} available.")
                return  

            # Fetch question data safely
            question_data = self.quiz_data[self.current_question_index]
            correct_answer_clean = clean_option(question_data["correct_answer"])
            selected_option_clean = clean_option(selected_option)

            # Compare the cleaned selected option with the correct answer
            if selected_option_clean == correct_answer_clean:
                self.score += 1
                self.custom_message_box(
                    "Correct!",
                    "Great job! You got the answer right.",
                    "correct.png",
                    "correct.mp3"
                )
            else:
                self.custom_message_box(
                    "Incorrect",
                    f"Sorry! The correct answer was: {question_data['correct_answer']}.",
                    "incorrect.png",
                    "incorrect.mp3"
                )

            # Move to the next question
            self.current_question_index += 1

        # **Re-check before calling show_question**
        if self.current_question_index < len(self.quiz_data):
            self.show_question()
        else:
            print("Quiz completed! No more questions.")
            self.end_quiz()

    def end_quiz(self):
        """Handle the end of the quiz and exit the application after showing the message for 10 seconds."""

        def show_message():
            """Show the final score message, wait for 10 seconds, then exit."""
            self.custom_message_box(
                title="Quiz Completed",
                message=f"Congratulations! You've completed the quiz. Your final score is {self.score}/{len(self.quiz_data)}.",
                image_path="congratulations.png",
                sound_path="congratulations.mp3",
                close_after=10  # Ensure this parameter is being used
            )

            # Schedule exit_application after 10 seconds (10000 milliseconds)
            self.window.after(10000, self.exit_application)

        # Hide the main quiz window
        self.window.withdraw()  

        # Close the quiz frame
        self.quiz_frame.pack_forget()

        # Destroy quiz window if it exists
        if hasattr(self, "quiz_window"):
            self.quiz_window.destroy()

        # Show the message and delay exit
        show_message()

    def show_time_up_message(self, correct_answer):
        """Handle the 'time up' message."""
        self.custom_message_box(
            "Time's Up",
            f"Your time is up! The correct answer was: {correct_answer}.",
            "time_up.png",
            "incorrect.mp3",
            callback=lambda: self.next_question(skip_message_box=True)  # Skip the next message box
        )

    def exit_application(self):
        """Exit the application safely."""
        print("Exiting application...")  # Debugging print (optional)
        self.window.quit()  # Stop the Tkinter main loop
        self.window.destroy()  # Destroy the window completely
        sys.exit()  # Ensure the script exits properly

# Assuming `bot_backend` is a predefined object that fetches quiz data
# bot_backend = SomeBackendClass()
# quiz_bot = QuizBotFrontend(bot_backend)
# quiz_bot.window.mainloop()