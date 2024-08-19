import customtkinter as ctk
from gradio_client import Client
from microsoft_tts import edge_tts_pipeline
import threading
import simpleaudio as sa
import speech_recognition as sr
from deep_translator import GoogleTranslator
import json
import os
import platform
from dotenv import load_dotenv
from dotenv import dotenv_values
load_dotenv()  
client = None
config = dotenv_values(".env")
username=config['USERNAME']
password=config['PASSWORD']
def clear_terminal():
    """
    Clears the terminal screen based on the operating system.
    """
    system = platform.system()
    
    if system == "Windows":
        os.system('cls')
    elif system == "Linux" or system == "Darwin":  # Darwin is macOS
        os.system('clear')
    else:
        raise OSError(f"Unsupported operating system: {system}")
def notification_sound(filename):
    # filename = "./okay.wav"
    wave_obj = sa.WaveObject.from_wave_file(filename)
    play_obj = wave_obj.play()
    play_obj.wait_done()
# Initialize the app
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Llama-3.1-8B Assistant")
        self.geometry("540x450")  # Adjusted size for the main window

        # Variables
        self.system_role = """You are a helpful Assistant, friendly and fun,
providing users with short and concise answers to their requests."""
        self.app_url = ""
        self.Language = "English"
        self.running_event = threading.Event()
        self.recognition_thread = None
        self.recognition_lock = threading.Lock()

        # Configure grid columns and rows
        self.grid_columnconfigure(0, weight=1)  # Left padding column
        self.grid_columnconfigure(1, weight=2)  # Main content column
        self.grid_columnconfigure(2, weight=1)  # Right padding column
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=0)  # Adjusted weight for buttons
        self.grid_rowconfigure(4, weight=0)  # Adjusted weight for buttons
        self.grid_rowconfigure(5, weight=1)  # Output area

        # App URL
        self.url_label = ctk.CTkLabel(self, text="App URL:")
        self.url_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.url_entry = ctk.CTkEntry(self, width=400)
        self.url_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # System Role
        self.role_label = ctk.CTkLabel(self, text="System Role:")
        self.role_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.role_entry = ctk.CTkTextbox(self, width=400, height=100)
        self.role_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.role_entry.insert("0.0", self.system_role)

        # Language Dropdown
        self.language_label = ctk.CTkLabel(self, text="Language:")
        self.language_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        self.language_var = ctk.StringVar(value="English")
        self.language_dropdown = ctk.CTkComboBox(self, values=['English', 'Hindi', 'Bengali', 'Afrikaans', 'Amharic', 
                                                               'Arabic', 'Azerbaijani', 'Bulgarian', 'Bosnian', 'Catalan', 
                                                               'Czech', 'Welsh', 'Danish', 'German', 'Greek', 'Spanish', 
                                                               'French', 'Irish', 'Galician', 'Gujarati', 'Hebrew', 'Croatian', 
                                                               'Hungarian', 'Indonesian', 'Icelandic', 'Italian', 'Japanese', 
                                                               'Javanese', 'Georgian', 'Kazakh', 'Khmer', 'Kannada', 'Korean', 
                                                               'Lao', 'Lithuanian', 'Latvian', 'Macedonian', 'Malayalam', 
                                                               'Mongolian', 'Marathi', 'Malay', 'Maltese', 'Burmese', 
                                                               'Norwegian Bokmål', 'Nepali', 'Dutch', 'Polish', 'Pashto', 
                                                               'Portuguese', 'Romanian', 'Russian', 'Sinhala', 'Slovak', 
                                                               'Slovenian', 'Somali', 'Albanian', 'Serbian', 'Sundanese', 
                                                               'Swedish', 'Swahili', 'Tamil', 'Telugu', 'Thai', 'Turkish', 
                                                               'Ukrainian', 'Urdu', 'Uzbek', 'Vietnamese', 'Chinese', 'Zulu'], 
                                                variable=self.language_var, width=400)
        self.language_dropdown.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        
        # Buttons
        self.submit_button = ctk.CTkButton(self, text="Start", command=self.start_app, width=100)
        self.submit_button.grid(row=3, column=1, padx=10, pady=5, sticky="ew")  # Centered in column 1

        self.stop_button = ctk.CTkButton(self, text="Stop", command=self.stop_app, width=100)
        self.stop_button.grid(row=4, column=1, padx=10, pady=5, sticky="ew")  # Centered in column 1

        # Output Display
        self.output_textbox = ctk.CTkTextbox(self, width=500, height=100, state='normal')
        self.output_textbox.grid(row=5, column=0, columnspan=3, padx=10, pady=5, sticky="nsew")

        
    def start_app(self):
        global client
        self.app_url = self.url_entry.get()
        custom_role = self.role_entry.get("1.0", "end").strip()
        if custom_role:
            self.system_role = custom_role
        self.Language = self.language_var.get()

        # self.update_output(f"App URL: {self.app_url}")
        # self.update_output(f"System Role: {self.system_role}")
        # self.update_output(f"Language: {self.Language}")

        try:
            # client = Client(self.app_url)
            client = Client(self.app_url,auth=[username, password])
            self.update_output(f"Connected to the server at {self.app_url}.")
        except:
            self.update_output("Error: Could not connect to the server. Please make sure the URL is correct and the server is running.")
            notification_sound("./notification/server_error.wav")
            return

        self.running_event.set()
        if self.recognition_thread and self.recognition_thread.is_alive():
            self.stop_app()  # Ensure any previous thread is stopped

        self.recognition_thread = threading.Thread(target=self.run_recognition)
        self.recognition_thread.start()

    def stop_app(self):
        self.running_event.clear()  # Signal the thread to stop
        if self.recognition_thread:
            # Wait for the thread to finish its current task
            with self.recognition_lock:
                self.recognition_thread.join()  
        self.update_output("Recognition stopped.")

    def run_recognition(self):
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 2000
        recognizer.pause_threshold = 1
        recognizer.phrase_threshold = 0.1
        recognizer.dynamic_energy_threshold = True
        calibration_duration = 1
        timeout = 10
        phrase_time_limit = None

        with open('language_code.json') as f:
            languages = json.load(f)

        def translate_text(text, Language):
            target_language = languages[Language]
            if Language == "Chinese":
                target_language = 'zh-CN'
            translator = GoogleTranslator(target=target_language)
            return translator.translate(text.strip())

        

        def tts(text, Language='English', tts_save_path=''):
            Gender = "Female"
            translate_text_flag = True
            no_silence = False
            speed = 1
            long_sentence = False                          
            edge_save_path = edge_tts_pipeline(text, Language, Gender, translate_text_flag=translate_text_flag, 
                                               no_silence=no_silence, speed=speed, tts_save_path=tts_save_path, 
                                               long_sentence=long_sentence)
            # self.update_output(f"Audio File Save at: {edge_save_path}")
            return edge_save_path

        def play_audio(text, Language='English'):
            filename = 'temp.wav'
            tts(text, Language=Language, tts_save_path=filename)
            if Language != "English":
                self.update_output(f"Translating Llama Response to {Language}:")
            else:
                self.update_output("Llama Response:")
            with open("temp.txt", "r" , encoding='utf-8') as f:
                self.update_output(f"{f.read()}")
            wave_obj = sa.WaveObject.from_wave_file(filename)
            play_obj = wave_obj.play()
            play_obj.wait_done()
            
        def chatbot(user_msg, Language='English'):
            try:
                llama_response = client.predict(self.system_role, user_msg, api_name="/predict")
            except:
                self.update_output("Error: Could not connect to the server. Please make sure the URL is correct and the server is running.")
                notification_sound("./notification/server_error.wav")
            play_audio(llama_response, Language)

        while self.running_event.is_set():    
            try:
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=calibration_duration)
                    self.update_output("\nListening...")
                    notification_sound("./notification/okay.wav")
                    audio_data = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                    MyText = recognizer.recognize_google(audio_data, language=languages[self.Language])
                    # MyText = MyText.lower()
                    self.update_output(f"Recognized Text: {MyText}")
                    usr_msg = translate_text(MyText, "English") if self.Language != "English" else MyText
                    if self.Language != "English":
                        self.update_output(f"English Text: {usr_msg}")
                    chatbot(usr_msg, self.Language)
                        
            except:
                continue

    def update_output(self, text):
        self.output_textbox.configure(state='normal')
        # self.output_textbox.tag_configure("colored", foreground=color)
        self.output_textbox.insert("end", text + "\n")
        self.output_textbox.yview_moveto(1)  # Scroll to the bottom
        self.output_textbox.configure(state='disabled')

if __name__ == "__main__":
    app = App()
    app.mainloop()
