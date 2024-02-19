import os
from pipes import quote
import re
import sqlite3
import struct
import subprocess
import time
import webbrowser
import pyaudio
import pyautogui
import pyjokes # joke function
from playsound import playsound
import eel

from engine.command import speak 
from engine.config import ASSISTANT_NAME


# intro play assistant function
import pywhatkit as kit
import pvporcupine

from engine.helper import extract_yt_term, remove_words

conn = sqlite3.connect("clara.db")
cursor = conn.cursor()


@eel.expose #somehow not working with live server
def playAssistantSound():
    music_dir = "www\\assets\\audio\\start_sound.mp3"
    playsound(music_dir)
    
def openCommand(query): # opening apps and website 
    query = query.replace(ASSISTANT_NAME, "")
    query = query.replace("open","")
    query.lower()
    
    app_name = query.strip()
    
    if app_name != "":

        try:
            cursor.execute(
                'SELECT path FROM sys_command WHERE name IN (?)', (app_name,))
            results = cursor.fetchall()

            if len(results) != 0:
                speak("Opening "+query)
                os.startfile(results[0][0])

            elif len(results) == 0: 
                cursor.execute(
                'SELECT url FROM web_command WHERE name IN (?)', (app_name,))
                results = cursor.fetchall()
                
                if len(results) != 0:
                    speak("Opening "+query)
                    webbrowser.open(results[0][0])

                else:
                    speak("Opening "+query)
                    try:
                        os.system('start '+query)
                    except:
                        speak("not found")
        except:
            speak("some thing went wrong")

        
# def PlayYoutube(query): # function to play youtube on chrome
#     search_term = extract_yt_term(query)
#     speak("Playing "+search_term+" on YouTube")
#     kit.playonyt(search_term)
    
# def extract_yt_term(command):
#     pattern = r'play\s+(.*?)\s+on\s+youtube'  
#     match = re.search(pattern, command, re.IGNORECASE)
#     return match.group(1) if match else None

def PlayYoutube(query): # to play videos on youtube
    search_term = extract_yt_term(query)
    speak("Playing "+search_term+" on YouTube")
    kit.playonyt(search_term)
    
def joke(query = ''): # humor of clara
    pyjokes.get_joke('en','neutral', max_tokens= 50) 
    

# def hotword():  # NOT APPLICABLE DUE TO PRE TRAINED WORDS, STILL ACCESSIBLE IF UNCOMMENT
#     porcupine=None # WILL RUN WITH RUN.PY
#     paud=None
#     audio_stream=None
#     try:
       
#         # pre trained keywords    
#         porcupine=pvporcupine.create(keywords=["clara","alexa"]) 
#         paud=pyaudio.PyAudio()
#         audio_stream=paud.open(rate=porcupine.sample_rate,channels=1,format=pyaudio.paInt16,input=True,frames_per_buffer=porcupine.frame_length)
        
#         # loop for streaming
#         while True:
#             keyword=audio_stream.read(porcupine.frame_length)
#             keyword=struct.unpack_from("h"*porcupine.frame_length,keyword)

#             # processing keyword comes from mic 
#             keyword_index=porcupine.process(keyword)

#             # checking first keyword detetcted for not
#             if keyword_index>=0:
#                 print("hotword detected")

#                 # pressing shorcut key win+j
#                 import pyautogui as autogui
#                 autogui.keyDown("win")
#                 autogui.press("j")
#                 time.sleep(2)
#                 autogui.keyUp("win")
                
#     except:
#         if porcupine is not None:
#             porcupine.delete()
#         if audio_stream is not None:
#             audio_stream.close()
#         if paud is not None:
#             paud.terminate()

# Whatsapp feature finding contacts
def findContact(query):
    
    words_to_remove = [ASSISTANT_NAME, 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'wahtsapp', 'video']
    query = remove_words(query, words_to_remove)

    try:
        query = query.strip().lower()
        cursor.execute("SELECT mobile_no FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + query + '%', query + '%'))
        results = cursor.fetchall()
        print(results[0][0])
        mobile_number_str = str(results[0][0])

        if not mobile_number_str.startswith('+63'):
            mobile_number_str = '+63' + mobile_number_str

        return mobile_number_str, query
    except:
        speak('not exist in contacts')
        return 0, 0
    
# For call method
def whatsApp(mobile_no, message, flag, name):
    

    if flag == 'message':
        target_tab = 12
        clara_message = "message send successfully to "+name

    elif flag == 'call':
        target_tab = 7
        message = ''
        clara_message = "calling to "+name

    else:
        target_tab = 6
        message = ''
        clara_message = "staring video call with "+name


    # Encode the message for URL
    encoded_message = quote(message)
    print(encoded_message)
    # Construct the URL
    whatsapp_url = f"whatsapp://send?phone={mobile_no}&text={encoded_message}"

    # Construct the full command
    full_command = f'start "" "{whatsapp_url}"'

    # Open WhatsApp with the constructed URL using cmd.exe
    subprocess.run(full_command, shell=True)
    time.sleep(5)
    subprocess.run(full_command, shell=True)
    
    pyautogui.hotkey('ctrl', 'f')

    for i in range(1, target_tab):
        pyautogui.hotkey('tab')

    pyautogui.hotkey('enter')
    speak(clara_message)
    




