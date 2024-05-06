import speech_recognition as sr
from speak import speak
import pyautogui
import pywhatkit as kit
import smtplib
from datetime import datetime, timedelta
import time
import sqlite3
from tkinter import messagebox


def listen(callback_function):
    # Initialize recognizer
    recognizer = sr.Recognizer()

    while True:
        with sr.Microphone() as source:
            # print("Listening...")
            recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise
            audio = recognizer.listen(source)  # Listen to the microphone input , timeout=5, phrase_time_limit=10

        try:
            # print("Recognizing...")
            query = recognizer.recognize_google(audio)  # Recognize speech using Google Speech Recognition
            # print("You said:", query)
            callback_function(query)  # Call the callback function with the recognized text
        except sr.UnknownValueError:
            speak("Sorry, I could not understand what you said.")
        except sr.RequestError as e:
            speak("Sorry, an error occurred while processing your request:", e)


def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        # print("Listening...")
        # r.pause_threshold = 0.6  # 0.8
        r.adjust_for_ambient_noise(source)  # Adjust ambient noise
        audio = r.listen(source)

    try:
        # print("Recognizing...")
        query = r.recognize_google(audio, language="en")
        # print(f"user said: {query}")
    except sr.UnknownValueError:
        speak("Sorry, I couldn't understand what you said.")
        return "none"
    except sr.RequestError:
        speak("Sorry, I'm unable to process your request. Please try again later.")
        return "none"
    return query.lower()


def sendEmail(sender_email_address, email_key, receiver_email, message, id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT uid FROM  receiver WHERE receiver_email=?", (receiver_email,))
    if cursor.fetchone():
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(sender_email_address, email_key)
        server.sendmail(sender_email_address, receiver_email, message)
        server.close()
        speak("email has been sent")
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS email_data (uid	INTEGER NOT NULL,receiver_email	TEXT NOT NULL,message	TEXT NOT NULL,FOREIGN KEY(uid) REFERENCES users(id));")
        try:
            cursor.execute("INSERT INTO email_data (uid, receiver_email, message) VALUES (?, ?, ?)",
                           (id, receiver_email, message))
            conn.commit()
            conn.close()
        except Exception as e:
            messagebox.showerror("Sqlite3 Error", f"Data could not be saved. {e}")
    else:
        messagebox.showerror("ID Error", "Receiver ID not exists")


def search_and_open_app(app_name):
    # Press Win + S to open the Windows search bar
    pyautogui.hotkey('win', 's')
    time.sleep(1)  # Wait for the search bar to open

    # Type the name of the application in the search bar
    pyautogui.write(app_name, interval=0.1)  # Adjust interval if necessary

    # Press Enter to perform the search
    pyautogui.press('enter')
    time.sleep(2)  # Adjust sleep time based on your system's speed


def process_text(query, id):
    query = query.lower()

    if "send message" in query:
        name = "".join(query.split("send message to ")[1:]).strip()
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM  whatsapp WHERE receiver_name=?", (name,))
        if cursor.fetchone():
            cursor.execute("SELECT receiver_mobile_number FROM  whatsapp WHERE receiver_name=?", (name,))
            numbertuple = cursor.fetchone()
            number = numbertuple[0]
            speak("What should I say?")
            message = takeCommand()
            current_time = datetime.now()

            # Calculate the time after one minute
            one_minute_later = current_time + timedelta(minutes=1)

            # Extract hour and minute from the one minute later time
            hour = one_minute_later.hour
            minute = one_minute_later.minute
            try:
                kit.sendwhatmsg(number, message, hour, minute)
            except:
                messagebox.showerror("Exception", "Please try again")
            conn.commit()
            conn.close()

        else:
            messagebox.showerror("Error", "number is not exists in database.")

    elif "send email" in query:
        name = "".join(query.split("send email to ")[1:]).strip()
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT email_address FROM  email WHERE uid=?  ", (id,))
            if cursor.fetchone():
                cursor.execute("SELECT email_address FROM  email WHERE uid=?  ", (id,))
                sender_email_address_tuple = cursor.fetchone()
                sender_email_address = sender_email_address_tuple[0]
                cursor.execute("SELECT email_key FROM  email WHERE uid=?  ", (id,))
                email_key_tuple = cursor.fetchone()
                email_key = email_key_tuple[0]
                conn.commit()
                cursor.execute("SELECT receiver_email FROM  receiver WHERE uid=? AND receiver_name=? ", (id, name))
                if cursor.fetchone():
                    cursor.execute("SELECT receiver_email FROM  receiver WHERE uid=? AND receiver_name=? ", (id, name))
                    receiver_email_tuple = cursor.fetchone()
                    receiver_email = receiver_email_tuple[0]
                    conn.commit()
                    try:
                        speak("what should I say?")
                        message = takeCommand()
                        conn.close()
                        sendEmail(sender_email_address, email_key, receiver_email, message, id)
                    except Exception as e:
                        cursor.close()
                        messagebox.showerror("sendEmail Error", f"Error in sending email: {e}", )

                else:

                    messagebox.showerror("Receiver Error", "Receiver email not exists.")
            else:
                messagebox.showerror("ID Error", "ID not exists.")
        except Exception as e:
            messagebox.showerror("Email Error", f"Please first add email and key \n {e}")


    elif "search on google" in query:
        try:
            speak("what should I say?")
            google_prompt = takeCommand()
            kit.search(google_prompt)

        except sr.UnknownValueError:
            speak("Sorry, I couldn't understand what you said.")
        except sr.RequestError:
            speak("Sorry, there was an error processing your request.")

    elif "search on youtube" in query:
        speak("What should I search for on YouTube?")
        search_query = takeCommand().lower()
        kit.playonyt(search_query)


    elif "open" in query:

        query = "".join(query.split("open")[1:]).strip()
        search_and_open_app(query)



    elif "you can rest now" in query:
        speak("Thanks for using me")
        quit()


    else:
        speak(f"No action defined for: {query}")
