from gradio_client import Client
from microsoft_tts import edge_tts_pipeline
app_url="https://ac2705c7493sff6327fff6.gradio.live/" 
system_role="""You are a helpful Assistant, friendly and fun,
providing users with short and concise answers to their requests."""

Language = "English" # @param ['English','Hindi','Bengali','Afrikaans', 'Amharic', 'Arabic', 'Azerbaijani', 'Bulgarian', 'Bosnian', 'Catalan', 'Czech', 'Welsh', 'Danish', 'German', 'Greek', 'Spanish', 'French', 'Irish', 'Galician', 'Gujarati', 'Hebrew', 'Croatian', 'Hungarian', 'Indonesian', 'Icelandic', 'Italian', 'Japanese', 'Javanese', 'Georgian', 'Kazakh', 'Khmer', 'Kannada', 'Korean', 'Lao', 'Lithuanian', 'Latvian', 'Macedonian', 'Malayalam', 'Mongolian', 'Marathi', 'Malay', 'Maltese', 'Burmese', 'Norwegian Bokmål', 'Nepali', 'Dutch', 'Polish', 'Pashto', 'Portuguese', 'Romanian', 'Russian', 'Sinhala', 'Slovak', 'Slovenian', 'Somali', 'Albanian', 'Serbian', 'Sundanese', 'Swedish', 'Swahili', 'Tamil', 'Telugu', 'Thai', 'Turkish', 'Ukrainian', 'Urdu', 'Uzbek', 'Vietnamese', 'Chinese', 'Zulu']
#make sure app_url ends with a slash
try:
    client = Client(app_url)
except:
    print("Error: Could not connect to the server. Please make sure the URL is correct and the server is running.")

def llama_api(system_role,user_msg):
    global client
    result = client.predict(
        system_role,
        user_msg,
        api_name="/predict"
    )
    return result

def tts(text,Language='English',tts_save_path=''):
    # text = "a quick brown fox jumps over the lazy dog and the dog barks loudly"
    # Language = "English" # @param ['English','Hindi','Bengali','Afrikaans', 'Amharic', 'Arabic', 'Azerbaijani', 'Bulgarian', 'Bosnian', 'Catalan', 'Czech', 'Welsh', 'Danish', 'German', 'Greek', 'Spanish', 'French', 'Irish', 'Galician', 'Gujarati', 'Hebrew', 'Croatian', 'Hungarian', 'Indonesian', 'Icelandic', 'Italian', 'Japanese', 'Javanese', 'Georgian', 'Kazakh', 'Khmer', 'Kannada', 'Korean', 'Lao', 'Lithuanian', 'Latvian', 'Macedonian', 'Malayalam', 'Mongolian', 'Marathi', 'Malay', 'Maltese', 'Burmese', 'Norwegian Bokmål', 'Nepali', 'Dutch', 'Polish', 'Pashto', 'Portuguese', 'Romanian', 'Russian', 'Sinhala', 'Slovak', 'Slovenian', 'Somali', 'Albanian', 'Serbian', 'Sundanese', 'Swedish', 'Swahili', 'Tamil', 'Telugu', 'Thai', 'Turkish', 'Ukrainian', 'Urdu', 'Uzbek', 'Vietnamese', 'Chinese', 'Zulu']
    Gender = "Female"# @param ['Male', 'Female']
    translate_text_flag=True
    no_silence=False
    speed=1
    # tts_save_path='temp.wav'
    long_sentence=False                          
    edge_save_path=edge_tts_pipeline(text,Language,Gender,translate_text_flag=translate_text_flag,no_silence=no_silence,speed=speed,tts_save_path=tts_save_path,long_sentence=long_sentence)
    print(f"Audio File Save at: {edge_save_path}")
    return edge_save_path

def notification_sound():
    filename="./okay.wav"
    wave_obj = sa.WaveObject.from_wave_file(filename)
    play_obj = wave_obj.play()
    play_obj.wait_done()

import simpleaudio as sa
def play_audio(text,Language='English'):
    filename='temp.wav'
    print(Language)
    tts(text,Language=Language,tts_save_path=filename)
    wave_obj = sa.WaveObject.from_wave_file(filename)
    play_obj = wave_obj.play()
    play_obj.wait_done()
    
def chatbot(user_msg,Language='English'):
    global system_role
    # user_msg="What is the weather like today?"
    llama_response=llama_api(system_role,user_msg)
    print(llama_response)
    play_audio(llama_response,Language)

# chatbot("what is 2+2 ?"Language)
import speech_recognition as sr
from deep_translator import GoogleTranslator

import json
with open('language_code.json') as f:
    languages = json.load(f)
# Language='Bengali'# @param ['English','Hindi','Bengali','Afrikaans', 'Amharic', 'Arabic', 'Azerbaijani', 'Bulgarian', 'Bosnian', 'Catalan', 'Czech', 'Welsh', 'Danish', 'German', 'Greek', 'Spanish', 'French', 'Irish', 'Galician', 'Gujarati', 'Hebrew', 'Croatian', 'Hungarian', 'Indonesian', 'Icelandic', 'Italian', 'Japanese', 'Javanese', 'Georgian', 'Kazakh', 'Khmer', 'Kannada', 'Korean', 'Lao', 'Lithuanian', 'Latvian', 'Macedonian', 'Malayalam', 'Mongolian', 'Marathi', 'Malay', 'Maltese', 'Burmese', 'Norwegian Bokmål', 'Nepali', 'Dutch', 'Polish', 'Pashto', 'Portuguese', 'Romanian', 'Russian', 'Sinhala', 'Slovak', 'Slovenian', 'Somali', 'Albanian', 'Serbian', 'Sundanese', 'Swedish', 'Swahili', 'Tamil', 'Telugu', 'Thai', 'Turkish', 'Ukrainian', 'Urdu', 'Uzbek', 'Vietnamese', 'Chinese', 'Zulu']

def translate_text(text, Language):
    global languages    
    # print("calling translate")
    target_language=languages[Language]
    if Language == "Chinese":
          target_language='zh-CN'
    translator = GoogleTranslator(target=target_language)
    translation = translator.translate(text.strip())
    t_text=str(translation)
    # print(f"{t_text}---{Language}----{target_language}")
    return t_text

recognizer = sr.Recognizer()
recognizer.energy_threshold = 2000
recognizer.pause_threshold = 1
recognizer.phrase_threshold = 0.1
recognizer.dynamic_energy_threshold = True
calibration_duration=1
timeout=10
phrase_time_limit=None



while True:	
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=calibration_duration)
            print("Listening...")
            notification_sound()
            audio_data = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            MyText =recognizer.recognize_google(audio_data,language=languages[Language])
            MyText = MyText.lower()
            print("Recognized text: "+MyText)
            if Language != "English":
                usr_msg=translate_text(MyText, "English")
            else:
                usr_msg=MyText

            #call the bot when you say "meata" 
            # pronunciations = ["meta","meta ai"]  # Add any variations you want to consider

            # matching_variation = next((variation for variation in pronunciations if variation in MyText.lower()), None)
            matching_variation=True
            if matching_variation:
                print("Send text: "+usr_msg)                        
                chatbot(usr_msg,Language)
            
    except:
        continue

