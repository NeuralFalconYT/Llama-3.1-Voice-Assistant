# Llama-3.1 Voice Assistant 

## Step 1: Run Hermes-3-Llama-3.1-8B as Llama-3.1 Gradio API
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NeuralFalconYT/Llama-3.1-Virtual-Assistant/blob/main/Hermes_3_Llama_3_1_8B_API.ipynb) <br>
Why choose [Hermes-3-Llama-3.1-8B](https://huggingface.co/NousResearch/Hermes-3-Llama-3.1-8B) instead of Llama-3.1-8B?<br>
Because the response time is faster than Llama-3.1-8B.

## Step 2: Clone the Repository or Download ZIP
To clone the repository:
```
git clone https://github.com/NeuralFalconYT/Llama-3.1-Voice-Assistant.git
```
```
cd Llama-3.1-Virtual-Assistant
```
Alternatively, download the ZIP file, extract the folder, and navigate to it:
```
cd Llama-3.1-Virtual-Assistant
```
## Step 3: Install Required Packages
My Python version is ```Python 3.10```<br>
Install the necessary packages:
```
pip install -r requirements.txt
```
```
pip install PyAudio
```
[Fix PyAudio Installation Error](https://youtu.be/rIFL4vtX0iA?si=jtJwhCOAN5Okx8J-)
## Step 4: Create a .env File
Create a .env file and paste your username and password from the Colab notebook. 
![colab](https://github.com/user-attachments/assets/20c36df7-056d-48b5-b512-74f1285e8822)

The format should be:
```
USERNAME=admin
PASSWORD=admin
```
## Step 5: Run the GUI
You can use this template for any chatbot hosted on Gradio, where you have 'system role' and 'user message' as inputs and the model's response as the output.

To start the GUI, run:
```
python GUI.py
```
![app](https://github.com/user-attachments/assets/2c9ed26a-07ae-4c54-83c2-6bb038bbdd37)
#### App URL:
You can find the App URL in the Colab Notebook.
![colab](https://github.com/user-attachments/assets/20c36df7-056d-48b5-b512-74f1285e8822)
#### System Role:
Enter your desired system role.
#### Language:
Select the language in which you want to communicate.
#### Gender:
Select the Gender for Edge Text to Speech.

Click the ```Start``` button to begin interacting with the virtual assistant.
Click the ```Stop``` button to end the interaction. Please note that it might take some time for the process to stop — just be patient.
## Step 6: Get Talking Head Avatar (Optional)
![Talking_Head_Avatar](https://github.com/user-attachments/assets/b1ea8927-f622-4b84-933e-13481a9ec199)<br>
Download [VMagicMirror](https://malaybaku.github.io/VMagicMirror/en/)<br>
Set up a VTUBER model & lip sync mic as Stereo Mix (Realtek(R) Audio)
## Step 7: Uninstall (Optional)
To uninstall, run:
```
pip uninstall -r requirements.txt
```
Then, delete the folder.
###### You can add your own TTS if you don't want to use Edge TTS. For that, you need to write code and either spend money to buy an API or use a faster open-source TTS.
![1](https://github.com/user-attachments/assets/315253c0-4c91-449f-81b0-dab0b028f040)
![2](https://github.com/user-attachments/assets/3972d13c-0513-4f87-b00a-9d9f75d089a0)
![3](https://github.com/user-attachments/assets/53f6e45f-8e85-4fc5-91e3-3daa0b9f23d1)
![4](https://github.com/user-attachments/assets/1f20a110-dc75-4528-b981-29b9b9f78f26)

## Acknowledgments

I would like to express my sincere gratitude to the following people and organizations:
- **[Hermes-3-Llama-3.1-8B]**: A special thanks to the creators of [[Hermes-3-Llama-3.1-8B](https://huggingface.co/NousResearch/Hermes-3-Llama-3.1-8B)] to Fine Tune the Llama-3.1.
- **[Anding Analytics]**: [[For Visualize Sound Code](https://youtu.be/675teI6-_-g?si=wT9mWgvrGRxasvNU)].


