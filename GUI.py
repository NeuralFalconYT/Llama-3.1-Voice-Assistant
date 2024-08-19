import customtkinter as ctk
from gradio_client import Client
from microsoft_tts import edge_tts_pipeline
import threading
import simpleaudio as sa
import speech_recognition as sr
from deep_translator import GoogleTranslator
import json

client = None

# Initialize the app
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Llama-3.1-8B Assistant")
        self.geometry("540x280")  # Adjusted size for the main window

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

    def start_app(self):
        global client
        self.app_url = self.url_entry.get()
        custom_role = self.role_entry.get("1.0", "end").strip()
        if custom_role:
            self.system_role = custom_role
        self.Language = self.language_var.get()

        print(f"App URL: {self.app_url}")
        print(f"System Role: {self.system_role}")
        print(f"Language: {self.Language}")
        try:
            client = Client(self.app_url)
        except:
            print("Error: Could not connect to the server. Please make sure the URL is correct and the server is running.")
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
        print("Recognition stopped.")

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

        def notification_sound():
            filename = "./okay.wav"
            wave_obj = sa.WaveObject.from_wave_file(filename)
            play_obj = wave_obj.play()
            play_obj.wait_done()

        def tts(text, Language='English', tts_save_path=''):
            Gender = "Female"
            translate_text_flag = True
            no_silence = False
            speed = 1
            long_sentence = False                          
            edge_save_path = edge_tts_pipeline(text, Language, Gender, translate_text_flag=translate_text_flag, 
                                               no_silence=no_silence, speed=speed, tts_save_path=tts_save_path, 
                                               long_sentence=long_sentence)
            print(f"Audio File Save at: {edge_save_path}")
            return edge_save_path

        def play_audio(text, Language='English'):
            filename = 'temp.wav'
            tts(text, Language=Language, tts_save_path=filename)
            wave_obj = sa.WaveObject.from_wave_file(filename)
            play_obj = wave_obj.play()
            play_obj.wait_done()

        def chatbot(user_msg, Language='English'):
            llama_response = client.predict(self.system_role, user_msg, api_name="/predict")
            print(llama_response)
            play_audio(llama_response, Language)

        while self.running_event.is_set():    
            try:
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=calibration_duration)
                    print("Listening...")
                    notification_sound()
                    audio_data = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                    MyText = recognizer.recognize_google(audio_data, language=languages[self.Language])
                    MyText = MyText.lower()
                    print("Recognized text: "+MyText)
                    usr_msg = translate_text(MyText, "English") if self.Language != "English" else MyText
                    chatbot(usr_msg, self.Language)
            except sr.RequestError:
                print("API was unreachable or unresponsive")
            except sr.UnknownValueError:
                print("Unable to recognize speech")

if __name__ == "__main__":
    app = App()
    app.mainloop()
