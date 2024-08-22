###
# Audio Wave sign code part copied from
#https://youtu.be/675teI6-_-g?si=wT9mWgvrGRxasvNU
###

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
from rich.console import Console
import pyaudio  # Added for real-time wave visualization
import math

console = Console()
load_dotenv()  
client = None
Gender="Female"
config = dotenv_values(".env")
username=config['USERNAME']
password=config['PASSWORD']
hexcode='#5ce65c'
import re
def clean_llm_text(text):
    bad_symbol = ['\n', '*', "\\'", '"', ':','-']
    for i in bad_symbol:
        if i in ['\n']:
            space = " "
        else:
            space = ""
        text = text.replace(i, space) 
    text=re.sub(r'\s*\([^)]*\)', '', text)
    return text.strip()
def notification_sound(filename):
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
        self.geometry("540x650")  # Adjusted height to accommodate the wave canvas

        # Variables
        self.system_role = """You are a helpful Assistant, friendly and fun,
providing users with short and concise answers to their requests."""
        self.app_url = ""
        self.Language = "English"
        self.Gender = "Female"  # Default gender value
        self.running_event = threading.Event()
        self.recognition_thread = None

        # Configure grid columns and rows
        self.grid_columnconfigure(0, weight=1)  # Left padding column
        self.grid_columnconfigure(1, weight=2)  # Main content column
        self.grid_columnconfigure(2, weight=1)  # Right padding column
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=0)
        self.grid_rowconfigure(4, weight=0)
        self.grid_rowconfigure(5, weight=0)
        self.grid_rowconfigure(6, weight=1)  # Output area
        self.grid_rowconfigure(7, weight=1)  # Wave visualization area

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
        
        # Gender Dropdown
        self.gender_label = ctk.CTkLabel(self, text="Gender:")
        self.gender_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        self.gender_var = ctk.StringVar(value="Female")  # Default gender value
        self.gender_dropdown = ctk.CTkComboBox(self, values=['Female', 'Male'], variable=self.gender_var, width=400)
        self.gender_dropdown.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
        
        # Buttons
        self.submit_button = ctk.CTkButton(self, text="Start", command=self.start_app, width=100)
        self.submit_button.grid(row=4, column=1, padx=10, pady=(5, 3), sticky="ew")

        self.stop_button = ctk.CTkButton(self, text="Stop", command=self.stop_app, width=100)
        self.stop_button.grid(row=5, column=1, padx=10, pady=(5, 10), sticky="ew")

        # Real-time Waveform Canvas
        self.canvas = ctk.CTkCanvas(self, width=500, height=150, bg="black")
        self.canvas.grid(row=6, column=0, columnspan=3, padx=10, pady=5, sticky="nsew")

        # Output Display
        self.output_textbox = ctk.CTkTextbox(self, width=500, height=100, state='normal')
        self.output_textbox.grid(row=7, column=0, columnspan=3, padx=10, pady=(5, 10), sticky="nsew")

        # pyaudio initialization for real-time visualization
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.FORMAT, channels=self.CHANNELS,
                                  rate=self.RATE, input=True,
                                  frames_per_buffer=self.CHUNK)

    def get_microphone_input_level(self):
        data = self.stream.read(self.CHUNK)
        rms = 0
        for i in range(0, len(data), 2):
            sample = int.from_bytes(data[i:i+2], byteorder='little', signed=True)
            rms += sample**2
        rms = math.sqrt(rms / self.CHUNK)
        return rms

    def hex_to_rgb(self, hex_code):
        hex_code = hex_code.strip('#')
        hex_list = [int(hex_code[i:i+2], 16) for i in (0, 2, 4)]
        rgb_tuple = tuple(hex_list)
        return rgb_tuple

    # def draw_sine_wave(self, amplitude):
    #     self.canvas.delete("all")
    #     points = []
    #     if amplitude > 10:
    #         for x in range(0, 500):
    #             y = 75 + int(amplitude * math.sin(x * 0.02))
    #             points.append((x, y))
    #     else:
    #         points.append((0, 75))
    #         points.append((500, 75))
        
    #     hex_code = '#5ce65c'
    #     self.canvas.create_line(points, fill=hex_code, width=2)

    def draw_sine_wave(self, amplitude):
        global hexcode
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        center_y = height / 2

        points = []
        if amplitude > 10:
            for x in range(0, width):
                # Generate y values based on a sine function and amplitude
                y = center_y + int(amplitude * math.sin(x * 0.02))
                points.append((x, y))
        else:
            points.append((0, center_y))
            points.append((width, center_y))
        
        # Draw the waveform line
        if len(points) > 1:
            self.canvas.create_line(points, fill=hexcode, width=2)

    def update_wave(self):
        amplitude_adjustment = self.get_microphone_input_level() / 50
        amplitude = max(10, amplitude_adjustment)
        self.draw_sine_wave(amplitude)
        self.after(17, self.update_wave)  # Update at ~60 FPS
    def stop_app(self):
        # Signal the thread to stop
        self.running_event.clear()
        
        # Properly close the audio stream and terminate PyAudio
        if self.stream and self.stream.is_active():
            self.stream.stop_stream()
            self.stream.close()

        # Terminate PyAudio instance if not already terminated
        if self.p:
            self.p.terminate()
            self.p = None

        # Update the UI to reflect that the app has stopped
        self.update_output("Recognition stopped.")

        # Ensure the thread is stopped without blocking the main thread
        if self.recognition_thread:
            self.recognition_thread = None


    def start_app(self):
        global client, Gender, username, password
        self.app_url = self.url_entry.get()
        custom_role = self.role_entry.get("1.0", "end").strip()
        if custom_role:
            self.system_role = custom_role
        self.Language = self.language_var.get()
        self.Gender = self.gender_var.get()
        Gender = self.Gender
        print(username)
        print(password)
        try:
            client = Client(self.app_url, auth=[str(username), str(password)])
            self.update_output(f"Connected to the server at {self.app_url} successfully.")
            console.print(f"Connected to the server at {self.app_url}.", style="bold green")
        except Exception as e:
            print(e)
            self.update_output("Error: Could not connect to the server. Please make sure the URL is correct and the server is running.")
            console.print("Error: Could not connect to the server. Please make sure the URL is correct and the server is running.", style="bold red")
            return

        self.running_event.set()
        if self.recognition_thread and self.recognition_thread.is_alive():
            self.stop_app()  # Ensure any previous thread is stopped

        # Reinitialize the audio stream
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.FORMAT, channels=self.CHANNELS,
                                rate=self.RATE, input=True,
                                frames_per_buffer=self.CHUNK)

        self.recognition_thread = threading.Thread(target=self.run_recognition)
        self.recognition_thread.start()

        # Start real-time waveform visualization
        self.update_wave()


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
            global Gender
            translate_text_flag = True
            no_silence = False
            speed = 1
            long_sentence = False                          
            edge_save_path = edge_tts_pipeline(text, Language, Gender, translate_text_flag=translate_text_flag, 
                                                no_silence=no_silence, speed=speed, tts_save_path=tts_save_path, 
                                                long_sentence=long_sentence)
            return edge_save_path

        def play_audio(text, Language='English'):
            global hexcode
            filename = 'temp.wav'
            text=clean_llm_text(text)
            tts(text, Language=Language, tts_save_path=filename)
            if Language != "English":
                self.update_output(f"Translating Llama Response to {Language}:")
                console.print(f"Translating Llama Response to {Language}:")
            else:
                self.update_output("Llama Response:")
                console.print(f"[bold green]Llama Response:[/bold green]")
            meta_response=""
            with open("temp.txt", "r", encoding='utf-8') as f:
                meta_response=f.read()
            print(meta_response)
            self.update_output(f"{meta_response}")
            hexcode="#0081f9"
            wave_obj = sa.WaveObject.from_wave_file(filename)
            play_obj = wave_obj.play()
            play_obj.wait_done()
            hexcode='#5ce65c'

        def chatbot(user_msg, Language='English'):
            global hexcode
            try:
                llama_response = client.predict(self.system_role, user_msg, api_name="/predict")
            except:
                self.update_output("Error: Could not connect to the server. Please make sure the URL is correct and the server is running.")
                console.print("Error: Could not connect to the server. Please make sure the URL is correct and the server is running.", style="bold red")
                hexcode="#d20a2e" 
                notification_sound("./notification/server_error.wav")
                hexcode='#5ce65c'
            play_audio(llama_response, Language)
        global hexcode
        while self.running_event.is_set():    
            try:
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=calibration_duration)
                    self.update_output("\nListening...")
                    console.print("\nListening...\n", style="bold red") 
                    hexcode="#d20a2e" 
                    notification_sound("./notification/okay.wav")
                    hexcode='#5ce65c'
                    audio_data = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                    MyText = recognizer.recognize_google(audio_data, language=languages[self.Language])
                    self.update_output(f"Recognized Text: {MyText}")
                    console.print(f"[bold green]Recognized Text:[/bold green] {MyText}", style="yellow")
                    usr_msg = translate_text(MyText, "English") if self.Language != "English" else MyText
                    if self.Language != "English":
                        self.update_output(f"English Text: {usr_msg}")
                        console.print(f"[bold green]English Text:[/bold green] {usr_msg}", style="yellow")
                    chatbot(usr_msg, self.Language)
                        
            except Exception as e:
                console.print(f"Error during recognition: {e}", style="bold red")
                continue

    def update_output(self, message):
        self.output_textbox.configure(state="normal")
        self.output_textbox.insert(ctk.END, message + "\n")
        self.output_textbox.configure(state="disabled")
        self.output_textbox.see(ctk.END)

    def on_closing(self):
        self.stop_app()
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()

