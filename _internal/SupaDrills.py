import customtkinter as ctk
import csv
from PIL import Image, ImageTk
import random
import json
import os
import re


SETTINGS_FILE = "_internal/settings.json"


DEFAULT_SETTINGS = {
    "NUM_QUESTIONS": 50,
    "TIMED_MODE": False,
    "TIMER_SECONDS": 10,
    "FULLSCREEN_MODE": False,
    "SHOW_ANSWER_DURATION": 1000,
    "APPEARANCE_MODE": "dark",
    "TOPIC_FILTER": "All Topics"
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                
                for key, value in DEFAULT_SETTINGS.items():
                    if key not in settings:
                        settings[key] = value
                return settings
        except (json.JSONDecodeError, IOError):
            return DEFAULT_SETTINGS.copy()
    else:
        return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    """Save settings to JSON file"""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
        return True
    except IOError:
        return False


settings = load_settings()


NUM_QUESTIONS = settings["NUM_QUESTIONS"]
TIMED_MODE = settings["TIMED_MODE"]
TIMER_SECONDS = settings["TIMER_SECONDS"]
FULLSCREEN_MODE = settings["FULLSCREEN_MODE"]
SHOW_ANSWER_DURATION = settings["SHOW_ANSWER_DURATION"]
TOPIC_FILTER = settings["TOPIC_FILTER"]
QUESTION_HISTORY = {}
ctk.set_appearance_mode(settings["APPEARANCE_MODE"])
ctk.set_default_color_theme('blue')

class Main(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Main Menu")
        self.geometry("1280x720")
        self.resizable(False,False)

        
        self.bgimg = ctk.CTkImage(light_image=Image.open("_internal/bg.png"), size=(600, 640))
        self.picframe = ctk.CTkFrame(self, width=600, height=640, corner_radius=20)
        self.picframe.place(relx=0.75, rely=0.5, anchor="center")
        self.bglabel = ctk.CTkLabel(self.picframe, image=self.bgimg, text='')
        self.bglabel.pack()

        
        self.mainframe = ctk.CTkFrame(self, width=600, height =640, corner_radius=20)
        self.mainframe.place(relx=0.25, rely = 0.5, anchor = "center")

        self.maintitle = ctk.CTkLabel(
            self.mainframe,
            text = "SUPADRILLS v1.3",
            font=("Verdana", 35, "bold"),
        )
        self.maintitle.place(relx=0.5, rely=0.1, anchor="center")


        self.quotetitle = ctk.CTkLabel(
            self.mainframe,
            text = "Even if you are not ready for the day, it cannot always be night\n -Donda West",
            font=("Verdana", 15,"italic"),
        )
        self.quotetitle.place(relx=0.5, rely=0.17, anchor="center")

        
        self.startbut = ctk.CTkButton(
            self.mainframe,
            text = "Start Drills",
            font=("Verdana", 18, "bold"),
            width=250, 
            height=75,
            corner_radius=20,
            command =self.start_ques
        )
        self.startbut.place(relx=0.5, rely=0.35, anchor="center")

        self.optionstbut = ctk.CTkButton(
            self.mainframe,
            text = "SUPAOPTIONS",
            font=("Verdana", 18, "bold"),
            width=250, 
            height=75,
            corner_radius=20,
            command = self.open_options
        )
        self.optionstbut.place(relx=0.5, rely=0.55, anchor="center")


        self.exitstbut = ctk.CTkButton(
            self.mainframe,
            text = "bye.",
            font=("Verdana", 18, "bold"),
            width=250, 
            height=75,
            corner_radius=20,
            fg_color = "#F82222",
            hover_color="#9B0404",
            command = self.quit
        )
        self.exitstbut.place(relx=0.5, rely=0.75, anchor="center")

    def start_ques(self):
        self.withdraw()
        self.openwin = runques()

    def open_options(self):
        self.withdraw()
        self.openoptions = OptionsWindow()


class runques(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.title("Select")
        self.geometry("600x640")
        self.resizable(False, False)

        self.mainframe = ctk.CTkFrame(self,width=590, height=630, corner_radius=20)
        self.mainframe.place(relx = 0.5, rely = 0.5, anchor = "center")

        self.title = ctk.CTkLabel(
            self.mainframe,
            text = "Select a Topic:",
            font=("Verdana", 18, "bold"),
        )
        self.title.place(relx = 0.5, rely = 0.05, anchor="center")

        ecetopics = {
            "MATH": "_internal/math_questions.csv",
            "GEAS": "_internal/geas_questions.csv",                      
            "ESAT": "_internal/esat_questions.csv",
            "ELECS": "_internal/electronics_questions.csv",
            "Ethics": "_internal/ethics_questions.csv",
            "R.A 9292": "_internal/ra9292_questions.csv",
        }
        ecttopics = {
            "ECTMATH": "_internal/ectmath_questions.csv",
            "ECT1": "_internal/ect001_questions.csv",                      
            "ECT2": "_internal/ect002_questions.csv"
        }

        y_pos = 0.2
        for topic, path in ecetopics.items():
            ctk.CTkButton(self.mainframe, text=topic, font=("Verdana", 18, "bold"),
                          width=200, height=50, corner_radius=20,
                          command=lambda p=path: self.start_quiz(p)
                          ).place(relx=0.25, rely=y_pos, anchor="center")
            y_pos += 0.1

        y2_pos = 0.2
        for topic1, path in ecttopics.items():
            ctk.CTkButton(self.mainframe, text=topic1, font=("Verdana", 18, "bold"),
                          width=200, height=50, corner_radius=20,
                          command=lambda p=path: self.start_quiz(p)
                          ).place(relx=0.75, rely=y2_pos, anchor="center")
            y2_pos += 0.1
class QuizWindow(ctk.CTkToplevel):
    def __init__(self, csv_path):
        super().__init__()
        self.title("Quiz")
        self.geometry("1280x720")
        self.csv_path = csv_path  
        
        if FULLSCREEN_MODE:
            self.attributes("-fullscreen", True)
        else:
            self.resizable(False, False)

        
        self.mainframe = ctk.CTkFrame(self, width=1250, height=680, corner_radius=20)
        self.mainframe.place(relx=0.5, rely=0.5, anchor="center")

        
        self.all_questions_exhausted = False
        self.questions_limited = False
        self.available_count = 0
        self.questions = self.load_questions(csv_path)
        
        
        if self.all_questions_exhausted:
            self.show_exhausted_message()
            return
        self.current_index = 0
        self.score = 0
        self.timer_job = None
        self.time_left = 0
        self.incorrect_questions = []  

        
        self.q_label = ctk.CTkLabel(self.mainframe, text="", wraplength=1000, font=("Verdana", 18))
        self.q_label.place(relx=0.5, rely=0.1, anchor="center")

        
        self.timer_label = ctk.CTkLabel(self.mainframe, text="", font=("Verdana", 20,"bold"))
        self.timer_label.place(relx=0.85, rely=0.93, anchor="center")

        
        self.feedback_label = ctk.CTkLabel(self.mainframe, text="", font=("Verdana", 14))
        self.feedback_label.place(relx=0.5, rely=0.18, anchor="center")

        
        self.choice_buttons = []
        y_positions = [0.35, 0.45, 0.55, 0.65]
        for i, y in enumerate(y_positions):
            btn = ctk.CTkButton(self.mainframe, text="", font=("Verdana", 15,"bold"),
                                width=400, height=50, corner_radius=10,
                                command=lambda idx=i: self.check_answer(idx))
            btn.place(relx=0.5, rely=y, anchor="center")
            self.choice_buttons.append(btn)

        
        self.score_label = ctk.CTkLabel(self.mainframe, text="Score: 0", font=("Verdana", 16, "bold"))
        self.score_label.place(relx=0.5, rely=0.8, anchor="center")

        
        filename = os.path.basename(csv_path)
        self.topic_label = ctk.CTkLabel(
            self.mainframe, 
            text=f"Topic: {filename.split('_')[0].upper()}",
            font=("Verdana", 12)
        )
        self.topic_label.place(relx=0.15, rely=0.93, anchor="center")

        
        ctk.CTkButton(self.mainframe, text="Return", font=("Verdana", 18, "bold"),
                      width=200, height=50, corner_radius=20,
                      fg_color="#F82222", hover_color="#9B0404",
                      command=self.return_to_main).place(relx=0.5, rely=0.93, anchor="center")

        self.show_question()

    def show_exhausted_message(self):
        """Show message when all questions have been exhausted"""
        
        for widget in self.mainframe.winfo_children():
            widget.destroy()
        
        
        exhausted_label = ctk.CTkLabel(
            self.mainframe,
            text="All Questions Exhausted!",
            font=("Verdana", 28, "bold"),
            text_color="orange"
        )
        exhausted_label.place(relx=0.5, rely=0.3, anchor="center")
        
        info_label = ctk.CTkLabel(
            self.mainframe,
            text="You've answered all available questions for this topic.\nWould you like to reset the question history and start over?",
            font=("Verdana", 18),
            wraplength=800,
            justify="center"
        )
        info_label.place(relx=0.5, rely=0.45, anchor="center")
        
        
        reset_btn = ctk.CTkButton(
            self.mainframe,
            text="Reset Questions & Start Over",
            font=("Verdana", 20, "bold"),
            width=300,
            height=60,
            corner_radius=20,
            fg_color="#28a745",
            hover_color="#218838",
            command=self.reset_questions_and_restart
        )
        reset_btn.place(relx=0.5, rely=0.6, anchor="center")
        
        
        return_btn = ctk.CTkButton(
            self.mainframe,
            text="Return to Main Menu",
            font=("Verdana", 18, "bold"),
            width=250,
            height=50,
            corner_radius=20,
            fg_color="#F82222",
            hover_color="#9B0404",
            command=self.return_to_main
        )
        return_btn.place(relx=0.5, rely=0.75, anchor="center")

    def reset_questions_and_restart(self):
        """Reset question history and restart the quiz"""
        topic = os.path.basename(self.csv_path)
        if topic in QUESTION_HISTORY:
            QUESTION_HISTORY[topic] = set()  
        
        
        self.destroy()
        QuizWindow(self.csv_path)

    def load_questions(self, csv_path):
        questions = []
        try:
            with open(csv_path, 'r', encoding='latin-1') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    questions.append(row)
            
            
            topic = os.path.basename(csv_path)
            if topic not in QUESTION_HISTORY:
                QUESTION_HISTORY[topic] = set()
            
            # Get questions that haven't been shown yet
            available_questions = [q for q in questions if self.get_question_id(q) not in QUESTION_HISTORY[topic]]
            
            # If we've exhausted all questions, return empty list to trigger reset prompt
            if not available_questions:
                self.all_questions_exhausted = True
                return []
            
            
            num_to_use = min(NUM_QUESTIONS, len(available_questions))
            if num_to_use < NUM_QUESTIONS:
                self.questions_limited = True
                self.available_count = num_to_use
            
            random.shuffle(available_questions)
            return available_questions[:num_to_use]
        except FileNotFoundError:
            print(f"Error: File {csv_path} not found.")
            return []

    def get_question_id(self, question):
        """Create a unique identifier for a question"""
        return hash(question['Question'].strip())  

    def show_question(self):
        
        if self.questions_limited and self.current_index >= len(self.questions):
            self.end_quiz_early()
            return
            
        if self.current_index < len(self.questions):
            q = self.questions[self.current_index]
            self.q_label.configure(text=f"Q{self.current_index + 1}: {q['Question']}")
            
            
            topic = os.path.basename(self.csv_path)
            question_id = self.get_question_id(q)
            if topic not in QUESTION_HISTORY:
                QUESTION_HISTORY[topic] = set()
            QUESTION_HISTORY[topic].add(question_id)
            
            
            choices = [q[f'Choice_{i}'] for i in range(1, 5)]
            random.shuffle(choices)
            q["shuffled_choices"] = choices

            
            for i, btn in enumerate(self.choice_buttons):
                btn.configure(text=choices[i])

            self.feedback_label.configure(text="")

            if TIMED_MODE:
                self.time_left = TIMER_SECONDS
                self.update_timer()
        else:
            self.end_quiz()

    def end_quiz_early(self):
        """End quiz early when limited questions available"""
        
        self.q_label.place_forget()
        self.feedback_label.place_forget()
        self.timer_label.place_forget()
        self.topic_label.place_forget()
        for btn in self.choice_buttons:
            btn.place_forget()

        
        limited_label = ctk.CTkLabel(
            self.mainframe,
            text=f"Limited Questions Available\n(Only {self.available_count} questions left)",
            font=("Verdana", 20, "bold"),
            text_color="orange"
        )
        limited_label.place(relx=0.5, rely=0.25, anchor="center")
        
        
        result_text = f"Quiz Completed!\nYour Score: {self.score}/{self.available_count}"
        result_label = ctk.CTkLabel(self.mainframe, text=result_text, font=("Verdana", 24, "bold"))
        result_label.place(relx=0.5, rely=0.4, anchor="center")

        
        reset_label = ctk.CTkLabel(
            self.mainframe,
            text="You've answered most available questions.\nReset to start over with all questions?",
            font=("Verdana", 16),
            wraplength=600,
            justify="center"
        )
        reset_label.place(relx=0.5, rely=0.55, anchor="center")
        
        
        reset_btn = ctk.CTkButton(
            self.mainframe,
            text="Reset All Questions",
            font=("Verdana", 16, "bold"),
            width=200,
            height=40,
            corner_radius=15,
            fg_color="#28a745",
            hover_color="#218838",
            command=self.reset_questions_and_restart
        )
        reset_btn.place(relx=0.5, rely=0.65, anchor="center")
        
        
        continue_btn = ctk.CTkButton(
            self.mainframe,
            text="Continue to Results",
            font=("Verdana", 16, "bold"),
            width=200,
            height=40,
            corner_radius=15,
            command=lambda: self.show_incorrect_questions(limited_label, result_label, reset_label, reset_btn, continue_btn)
        )
        continue_btn.place(relx=0.5, rely=0.75, anchor="center")

    def show_incorrect_questions(self, *widgets_to_remove):
        """Remove reset prompt widgets and show incorrect questions"""
        for widget in widgets_to_remove:
            widget.destroy()
        
        
        if self.incorrect_questions:
            scroll_frame = ctk.CTkScrollableFrame(self.mainframe, width=1000, height=300)
            scroll_frame.place(relx=0.5, rely=0.6, anchor="center")

            for i, item in enumerate(self.incorrect_questions, 1):
                            
                            q_label = ctk.CTkLabel(
                                scroll_frame,
                                text=f"{i}. {item['question']}",
                                font=("Verdana", 14, "bold"),
                                wraplength= 900,
                                justify="left"
                            )
                            q_label.pack(anchor="w", padx=20, pady=(10, 2))

                            
                            your_ans_label = ctk.CTkLabel(
                                scroll_frame,
                                text=f"   Your answer: {item['user_answer']}",
                                font=("Verdana", 13),
                                text_color="red",
                                wraplength= 900,
                                justify="left"
                            )
                            your_ans_label.pack(anchor="w", padx=40)

                            
                            correct_ans_label = ctk.CTkLabel(
                                scroll_frame,
                                text=f"   Correct answer: {item['correct_answer']}",
                                font=("Verdana", 13, "bold"),
                                text_color="green",
                                wraplength= 900,
                                justify="left"
                            )
                            correct_ans_label.pack(anchor="w", padx=40, pady=(0, 5))
        else:
            perfect_label = ctk.CTkLabel(
                self.mainframe, 
                text="Perfect! You answered all questions correctly!",
                font=("Verdana", 18),
                text_color="green"
            )
            perfect_label.place(relx=0.5, rely=0.5, anchor="center")


    def update_timer(self):
        if self.time_left > 0:
            self.timer_label.configure(text=f"Time: {self.time_left}s")
            self.time_left -= 1
            self.timer_job = self.after(1000, self.update_timer)
        else:
            self.timer_label.configure(text="Time's up!")
            self.after(500, self.next_question)

    def check_answer(self, choice_index):
        if self.timer_job:
            self.after_cancel(self.timer_job)

        q = self.questions[self.current_index]
        selected_choice = q["shuffled_choices"][choice_index]

        if selected_choice.strip() == q["Answer"].strip():
            self.feedback_label.configure(text="✅ Correct!", text_color="green")
            self.score += 1
        else:
            self.feedback_label.configure(
                text=f"❌ Wrong! Correct answer: {q['Answer']}",
                text_color="red"
            )
            self.incorrect_questions.append({
                'question': q['Question'],
                'user_answer': selected_choice,
                'correct_answer': q["Answer"]
            })

        self.score_label.configure(text=f"Score: {self.score}")
        for btn in self.choice_buttons:
            btn.configure(state="disabled")

        self.after(SHOW_ANSWER_DURATION, self.next_question)


    def next_question(self):
        self.current_index += 1
        
        for btn in self.choice_buttons:
            btn.configure(state="normal")
        self.show_question()

    def end_quiz(self):
        
        self.q_label.place_forget()
        self.feedback_label.place_forget()
        self.timer_label.place_forget()
        self.topic_label.place_forget()
        for btn in self.choice_buttons:
            btn.place_forget()

        
        result_text = f"Quiz Completed!\nYour Score: {self.score}/{len(self.questions)}"
        result_label = ctk.CTkLabel(self.mainframe, text=result_text, font=("Verdana", 24, "bold"))
        result_label.place(relx=0.5, rely=0.3, anchor="center")

        
        if self.incorrect_questions:
            scroll_frame = ctk.CTkScrollableFrame(self.mainframe, width=1000, height=300)
            scroll_frame.place(relx=0.5, rely=0.6, anchor="center")

            for i, item in enumerate(self.incorrect_questions, 1):
                
                q_label = ctk.CTkLabel(
                    scroll_frame,
                    text=f"{i}. {item['question']}",
                    font=("Verdana", 14, "bold"),
                    wraplength= 900,
                    justify="left"
                )
                q_label.pack(anchor="w", padx=20, pady=(10, 2))

                
                your_ans_label = ctk.CTkLabel(
                    scroll_frame,
                    text=f"   Your answer: {item['user_answer']}",
                    font=("Verdana", 13),
                    text_color="red",
                    wraplength= 900,
                    justify="left"
                )
                your_ans_label.pack(anchor="w", padx=40)

                
                correct_ans_label = ctk.CTkLabel(
                    scroll_frame,
                    text=f"   Correct answer: {item['correct_answer']}",
                    font=("Verdana", 13, "bold"),
                    text_color="green",
                    wraplength= 900,
                    justify="left"
                )
                correct_ans_label.pack(anchor="w", padx=40, pady=(0, 5))
        else:
            perfect_label = ctk.CTkLabel(
                self.mainframe, 
                text="Perfect! You answered all questions correctly!",
                font=("Verdana", 18),
                text_color="green"
            )
            perfect_label.place(relx=0.5, rely=0.5, anchor="center")
            
    def return_to_main(self):
        self.destroy()
        app.deiconify()


class OptionsWindow(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.title("SUPAOPTIONS")
        self.geometry("600x640")
        self.resizable(False, False)

        self.mainframe = ctk.CTkFrame(self, width=590, height=630, corner_radius=20)
        self.mainframe.place(relx=0.5, rely=0.5, anchor="center")

        self.title = ctk.CTkLabel(
            self.mainframe,
            text="SUPAOPTIONS",
            font=("Verdana", 24, "bold"),
        )
        self.title.place(relx=0.5, rely=0.05, anchor="center")

        
        self.numq_label = ctk.CTkLabel(
            self.mainframe,
            text="Number of Questions:",
            font=("Verdana", 16),
        )
        self.numq_label.place(relx=0.3, rely=0.15, anchor="center")

        self.numq_entry = ctk.CTkEntry(
            self.mainframe,
            width=100,
            height=30,
            font=("Verdana", 14),
        )
        self.numq_entry.place(relx=0.7, rely=0.15, anchor="center")
        self.numq_entry.insert(0, str(NUM_QUESTIONS))

        
        self.timed_var = ctk.BooleanVar(value=TIMED_MODE)
        self.timed_check = ctk.CTkCheckBox(
            self.mainframe,
            text="Timed Mode",
            variable=self.timed_var,
            font=("Verdana", 16),
            command=self.toggle_timer_options
        )
        self.timed_check.place(relx=0.3, rely=0.25, anchor="center")

        
        self.timer_label = ctk.CTkLabel(
            self.mainframe,
            text="Timer Duration (seconds):",
            font=("Verdana", 16),
        )
        self.timer_label.place(relx=0.3, rely=0.35, anchor="center")

        self.timer_entry = ctk.CTkEntry(
            self.mainframe,
            width=100,
            height=30,
            font=("Verdana", 14),
        )
        self.timer_entry.place(relx=0.7, rely=0.35, anchor="center")
        self.timer_entry.insert(0, str(TIMER_SECONDS))
        self.toggle_timer_options()  

        
        self.fullscreen_var = ctk.BooleanVar(value=FULLSCREEN_MODE)
        self.fullscreen_check = ctk.CTkCheckBox(
            self.mainframe,
            text="Fullscreen Mode",
            variable=self.fullscreen_var,
            font=("Verdana", 16),
        )
        self.fullscreen_check.place(relx=0.3, rely=0.45, anchor="center")

        
        self.answer_duration_label = ctk.CTkLabel(
            self.mainframe,
            text="Answer Display (ms):",
            font=("Verdana", 16),
        )
        self.answer_duration_label.place(relx=0.3, rely=0.55, anchor="center")

        self.answer_duration_entry = ctk.CTkEntry(
            self.mainframe,
            width=100,
            height=30,
            font=("Verdana", 14),
        )
        self.answer_duration_entry.place(relx=0.7, rely=0.55, anchor="center")
        self.answer_duration_entry.insert(0, str(SHOW_ANSWER_DURATION))

        
        self.appearance_label = ctk.CTkLabel(
            self.mainframe,
            text="Appearance Mode:",
            font=("Verdana", 16),
        )
        self.appearance_label.place(relx=0.3, rely=0.65, anchor="center")

        self.appearance_var = ctk.StringVar(value=settings["APPEARANCE_MODE"].capitalize())
        self.appearance_option = ctk.CTkOptionMenu(
            self.mainframe,
            values=["Light", "Dark", "System"],
            variable=self.appearance_var,
            width=100
        )
        self.appearance_option.place(relx=0.7, rely=0.65, anchor="center")

        
        self.save_btn = ctk.CTkButton(
            self.mainframe,
            text="Save Settings",
            font=("Verdana", 18, "bold"),
            width=200,
            height=50,
            corner_radius=20,
            command=self.save_settings
        )
        self.save_btn.place(relx=0.5, rely=0.8, anchor="center")

        
        ctk.CTkButton(self.mainframe, text="Return", font=("Verdana", 18, "bold"),
                      width=200, height=50, corner_radius=20,
                      fg_color="#F82222", hover_color="#9B0404",
                      command=self.return_to_main).place(relx=0.5, rely=0.9, anchor="center")
        

    def toggle_timer_options(self):
        if self.timed_var.get():
            self.timer_entry.configure(state="normal")
            self.timer_label.configure(text_color="black")
        else:
            self.timer_entry.configure(state="disabled")
            self.timer_label.configure(text_color="gray")

    def save_settings(self):
        global NUM_QUESTIONS, TIMED_MODE, TIMER_SECONDS, FULLSCREEN_MODE, SHOW_ANSWER_DURATION
        
        try:
            
            NUM_QUESTIONS = int(self.numq_entry.get())
            TIMED_MODE = self.timed_var.get()
            TIMER_SECONDS = int(self.timer_entry.get())
            FULLSCREEN_MODE = self.fullscreen_var.get()
            SHOW_ANSWER_DURATION = int(self.answer_duration_entry.get())
            
            
            new_appearance = self.appearance_var.get().lower()
            ctk.set_appearance_mode(new_appearance)
            
            
            settings.update({
                "NUM_QUESTIONS": NUM_QUESTIONS,
                "TIMED_MODE": TIMED_MODE,
                "TIMER_SECONDS": TIMER_SECONDS,
                "FULLSCREEN_MODE": FULLSCREEN_MODE,
                "SHOW_ANSWER_DURATION": SHOW_ANSWER_DURATION,
                "APPEARANCE_MODE": new_appearance,
                "TOPIC_FILTER": TOPIC_FILTER
            })
            
            
            if save_settings(settings):
                self.show_feedback("Settings saved successfully!", "green")
            else:
                self.show_feedback("Error saving settings!", "red")
                
        except ValueError:
            self.show_feedback("Please enter valid numbers!", "red")

    def show_feedback(self, message, color):
        feedback = ctk.CTkLabel(
            self.mainframe,
            text=message,
            font=("Verdana", 14),
            text_color=color
        )
        feedback.place(relx=0.5, rely=0.75, anchor="center")
        self.after(2000, feedback.destroy)

    def return_to_main(self):
        self.destroy()
        app.deiconify()


if __name__ == "__main__":
    app = Main()
    app.mainloop()