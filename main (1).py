import customtkinter
from PIL import Image
import random
import sqlite3
import datetime
import smtplib
import re
from tkinter import messagebox
import ai
from speak import speak
import speech_recognition as sr
import hashlib
from CTkMenuBar import *
import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class MiddleLeftFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        # home_button_image = customtkinter.CTkImage(Image.open("home.png"))
        # self.home_button = customtkinter.CTkButton(self, text="", width=32, image=home_button_image)
        self.home_button = customtkinter.CTkButton(self, text="?", width=32)
        self.home_button.pack(padx=1, pady=1, side="top")
        self.home_button = customtkinter.CTkButton(self, text="!", width=32)
        self.home_button.pack(padx=1, pady=1, side="top")


class MainProgram(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.main_frame = customtkinter.CTkFrame(self)
        self.main_frame.pack(expand=True, fill="both")

        self.login_button = customtkinter.CTkButton(self.main_frame, text="Login")
        self.login_button.place(relx=0.5, rely=0.45, anchor="center")

        self.signup_button = customtkinter.CTkButton(self.main_frame, text="Sign Up")
        self.signup_button.place(relx=0.5, rely=0.50, anchor="center")


class LoginAndSignupFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.main_frame = customtkinter.CTkFrame(self)
        self.main_frame.pack(expand=True, fill="both")

        self.login_button = customtkinter.CTkButton(self.main_frame, text="Login", command=self.show_login_frame)
        self.login_button.place(relx=0.5, rely=0.45, anchor="center")

        self.signup_button = customtkinter.CTkButton(self.main_frame, text="Sign Up", command=self.show_signup_frame)
        self.signup_button.place(relx=0.5, rely=0.50, anchor="center")

        self.login_frame = None
        self.signup_frame = None

    def show_login_frame(self):
        if self.login_frame is None:
            self.main_frame.pack_forget()

            self.login_frame = customtkinter.CTkFrame(self)
            self.login_frame.pack(expand=True, fill="both")

            self.login_label = customtkinter.CTkLabel(self.login_frame, text="Login Frame")
            self.login_label.pack(pady=10)

            self.user_entry = customtkinter.CTkEntry(self.login_frame, placeholder_text="Username")
            self.user_entry.place(relx=0.5, rely=0.35, anchor="center")

            self.user_pass = customtkinter.CTkEntry(self.login_frame, placeholder_text="Password", show="*")
            self.user_pass.place(relx=0.5, rely=0.40, anchor="center")

            self.login_button = customtkinter.CTkButton(self.login_frame, text="Login", command=self.login)
            self.login_button.place(relx=0.5, rely=0.45, anchor="center")

            self.close_button = customtkinter.CTkButton(self.login_frame, text="Back", command=self.close_login_frame)
            self.close_button.place(relx=0.5, rely=0.50, anchor="center")
            self.main_program = None
        else:
            self.close_login_frame()

    def close_login_frame(self):
        self.main_frame.pack(expand=True, fill="both")
        self.login_frame.pack_forget()
        self.login_frame = None

    def check_credentials(self, username, password):

        try:
            # Connect to the database
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            password_hash = self.hash_password(password)

            # Execute a query to check if the username and password exist
            cursor.execute("SELECT id FROM users WHERE username=? AND password_hash=?", (username, password_hash))
            id = cursor.fetchone()
            uid = id[0]
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS login_history (user_id	INTEGER NOT NULL,login_time	TEXT NOT NULL,FOREIGN KEY(user_id) REFERENCES users(id));")
            cursor.execute(
                "INSERT INTO login_history (user_id, login_time) VALUES (?, DATETIME('now', '+5 hours', '+30 minutes'));",
                (uid,))
            conn.commit()
            # Close the connection
            conn.close()

            # If row is not None, username and password exist in the database
            if id:
                return True
            else:
                return False
        except Exception as e:
            messagebox.showerror("Database Error",f"No such user exists.\n {e}")


    def login(self):

        username = self.user_entry.get()
        password = self.user_pass.get()
        if username == "" or password == "":
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        if self.check_credentials(username, password):

            if self.main_program is None:
                self.login_frame.pack_forget()

                def wish():
                    self.chat_history.configure(state="normal")
                    current_time = datetime.datetime.now().strftime("%I:%M %p")
                    current_hour = datetime.datetime.now().hour
                    if 6 <= current_hour < 12:
                        self.chat_history.insert(customtkinter.END, f"Good morning, it's {current_time} \n")

                    elif 12 <= current_hour < 18:
                        self.chat_history.insert(customtkinter.END, f"Good afternoon, it's {current_time} \n")

                    else:
                        self.chat_history.insert(customtkinter.END, f"Good evening, it's {current_time} \n")

                    self.chat_history.insert(customtkinter.END, f"Nayak here, what can I do for you?\n\n")

                    self.chat_history.configure(state="disabled")

                self.chat_history = customtkinter.CTkTextbox(self, wrap="word", state="disabled")
                self.chat_history.pack(padx=1, pady=1, expand=True, fill="both")

                self.user_input = customtkinter.CTkEntry(self)
                self.user_input.pack(padx=1, pady=1, side="left", fill="x", expand=True)

                self.send_button = customtkinter.CTkButton(self, text="Send", command=self.send_message)
                self.send_button.pack(padx=1, pady=1, side="left")

                # self.toggle_state = False

                self.voice = customtkinter.CTkButton(self, text="voice", command=self.listen_and_store)
                self.voice.pack(padx=1, pady=1, side="left")
                wish()

        else:
            messagebox.showerror("Error", "Wrong username or password")

    def listen_and_store(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            # print("Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio, language='en-in')
            text = text.lower()
            # print(text)
            if "nayak" in text:
                try:
                    self.chat_history.configure(state="normal")
                    # speak("Doing it Please wait")
                    text = "".join(text.split("nayak")[1:]).strip()
                    # print(text)

                    self.chat_history.insert(customtkinter.END, f"you: {text} \n")
                    username = self.user_entry.get()
                    conn = sqlite3.connect('users.db')
                    cursor = conn.cursor()
                    cursor.execute("SELECT id FROM  users WHERE username=?", (username,))
                    id = cursor.fetchone()
                    id = id[0]
                    conn.commit()
                    # Close the connection
                    conn.close()
                    # print(id)
                    # Get response from the chatbot
                    response = ai.ai(prompt=text, id=id)
                    self.chat_history.insert(customtkinter.END, f"Nayak: {response} \n\n")
                    self.chat_history.configure(state="disabled")
                except:
                    messagebox.showerror("Open AI Error", "Please add open ai key.")

            elif "tell me joke" in text:
                import pyjokes
                joke = pyjokes.get_joke()
                self.chat_history.configure(state="normal")
                self.chat_history.insert(customtkinter.END, f"Nayak: {joke} \n\n")
                self.chat_history.configure(state="disabled")
                speak(joke)

            else:

                from sub_main import process_text
                username = self.user_entry.get()
                conn = sqlite3.connect('users.db')
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM  users WHERE username=?", (username,))
                id = cursor.fetchone()
                id = id[0]
                conn.commit()

                conn.close()
                process_text(text, id)


        except sr.UnknownValueError:
            speak("Sorry, I could not understand what you said.")
        except sr.RequestError as e:
            speak(f"Could not request results from Google Speech Recognition service; {e}")

    def send_message(self):
        try:
            self.chat_history.configure(state="normal")

            message = self.user_input.get()
            self.user_input.delete(0, customtkinter.END)

            # Display user message in the chat history
            self.chat_history.insert(customtkinter.END, f"you: {message} \n")
            username = self.user_entry.get()
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM  users WHERE username=?", (username,))
            id = cursor.fetchone()
            id = id[0]
            conn.commit()
            # Close the connection
            conn.close()
            # print(id)
            # Get response from the chatbot
            response = ai.ai(prompt=message, id=id)
            # Display chatbot response in the chat history
            self.chat_history.insert(customtkinter.END, f"Nayak: {response} \n\n")
            self.chat_history.configure(state="disabled")

        except Exception as e:
            messagebox.showerror(f"Open AI Error", f"Please add open ai key. {e}")

    def show_signup_frame(self):
        if self.signup_frame is None:
            self.main_frame.pack_forget()

            self.signup_frame = customtkinter.CTkFrame(self)
            self.signup_frame.pack(expand=True, fill="both")

            self.user_name = customtkinter.CTkEntry(self.signup_frame, placeholder_text="Username")
            self.user_name.place(relx=0.5, rely=0.35, anchor="center")

            self.user_pass = customtkinter.CTkEntry(self.signup_frame, placeholder_text="Password", show="*")
            self.user_pass.place(relx=0.5, rely=0.40, anchor="center")

            self.user_email = customtkinter.CTkEntry(self.signup_frame, placeholder_text="xyz@gmail.com")
            self.user_email.place(relx=0.5, rely=0.45, anchor="center")

            self.generate_otp_button = customtkinter.CTkButton(self.signup_frame, text="Generate OTP",
                                                               command=self.generate_otp)
            self.generate_otp_button.place(relx=0.5, rely=0.50, anchor="center")

            self.enter_otp = customtkinter.CTkEntry(self.signup_frame, placeholder_text="000-000")
            # self.enter_otp.place(relx=0.5, rely=0.55, anchor="center")

            self.signup_button = customtkinter.CTkButton(self.signup_frame, text="Sign Up", command=self.signup)
            # self.signup_button.place(relx=0.5, rely=0.60, anchor="center")

            self.back_button = customtkinter.CTkButton(self.signup_frame, text="Back", command=self.close_signup_frame)
            self.back_button.place(relx=0.5, rely=0.70, anchor="center")
            self.main_program = None
            # self.check_entries()
        else:
            self.close_signup_frame()

    def hash_password(self, password):
        # Hash the password using SHA256
        return hashlib.sha256(password.encode()).hexdigest()

    def generate_otp(self):
        self.check_entries()

    def check_entries(self):
        username = self.user_name.get()
        email = self.user_email.get()
        password = self.user_pass.get()

        if username == "" or email == "" or password == "":
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        # Regular expression for email format validation
        email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

        if not re.match(email_regex, email):
            messagebox.showerror("Error", "Invalid email format.")
            return

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS users (id	INTEGER,username	TEXT NOT NULL UNIQUE,email	TEXT NOT NULL UNIQUE,password_hash	TEXT NOT NULL,PRIMARY KEY(id AUTOINCREMENT))")
        # Check if the username already exists
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        if cursor.fetchone():
            messagebox.showerror("Error", "Username already exists.")
            conn.close()
            return

        # Check if the email already exists
        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        if cursor.fetchone():
            messagebox.showerror("Error", "Email already exists.")
            conn.close()
            return

        # Hash the password
        self.password_hash = self.hash_password(password)
        self.otp = self.gn_otp()
        receiver_email_address = email
        self.send_email(receiver_email_address, self.otp)
        # print("Generated OTP:", self.otp)

        conn.commit()
        conn.close()

        messagebox.showinfo("OTP", "OTP send to your mail, " + username)

    def send_email(self, receiver_email, otp):
        email_address = "ffdon960@gmail.com"
        email_key = "vvrm mwrw wrkn rrnn"
        """Send OTP via email."""
        # Sender email configuration
        sender_email = email_address  # Replace with your email address
        password = email_key  # Replace with your email password
        # Email content
        subject = "OTP Verification"
        body = f"Your OTP is: {otp}"
        # SMTP server configuration
        smtp_server = "smtp.gmail.com"
        port = 587
        # Connect to SMTP server
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()  # Start TLS encryption
        server.login(sender_email, password)
        # Compose email
        message = f"Subject: {subject}\n\n{body}"
        # Send email
        server.sendmail(sender_email, receiver_email, message)
        self.enter_otp.place(relx=0.5, rely=0.55, anchor="center")
        self.signup_button.place(relx=0.5, rely=0.60, anchor="center")
        server.quit()

    def send_info(self):
        receiver_email = self.user_email.get()
        email_address = "ffdon960@gmail.com"
        email_key = "vvrm mwrw wrkn rrnn"
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id from users WHERE email = ?", (receiver_email,))
        uidtuple = cursor.fetchone()
        uid = uidtuple[0]
        # print(uid)
        conn.commit()
        conn.close()
        """Send OTP via email."""
        # Sender email configuration
        sender_email = email_address  # Replace with your email address
        password = email_key  # Replace with your email password
        # Email content
        subject = "ID information"
        body = (f"Your ID is: {uid}"
                f" Please remember it")
        # SMTP server configuration
        smtp_server = "smtp.gmail.com"
        port = 587
        # Connect to SMTP server
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()  # Start TLS encryption
        server.login(sender_email, password)
        # Compose email
        message = f"Subject: {subject}\n\n{body}"
        # Send email
        server.sendmail(sender_email, receiver_email, message)
        server.quit()

    def save_data(self):
        username = self.user_name.get()
        email = self.user_email.get()
        password = self.user_pass.get()
        password_hash = self.hash_password(password)

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                       (username, email, password_hash))
        conn.commit()
        conn.close()

    def signup(self):
        entered_otp = self.enter_otp.get().strip()
        if entered_otp == self.otp:
            # print("wel come")
            self.save_data()
            self.send_info()

            if self.main_program is None:
                self.signup_frame.pack_forget()
                self.show_login_frame()


        else:
            messagebox.showerror("Error", "Incorrect OTP!")

    def close_signup_frame(self):
        self.main_frame.pack(expand=True, fill="both")
        self.signup_frame.pack_forget()
        self.signup_frame = None

    def gn_otp(self):
        # Generate a 6-digit OTP
        return str(random.randint(100000, 999999))


class MiddleRightFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.login_and_signup_frame = LoginAndSignupFrame(self)
        self.login_and_signup_frame.pack(fill="both", padx=1, pady=1, expand=True)


class LeftFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.middle_left_frame = MiddleLeftFrame(self)
        self.middle_left_frame.pack(fill="y", padx=1, pady=1, side="left")
        self.middle_right_frame = MiddleRightFrame(self)
        self.middle_right_frame.pack(fill="both", padx=1, pady=1, side="left", expand=True)


class MainFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.left_frame = LeftFrame(self)
        self.left_frame.pack(fill="both", padx=1, pady=1, expand=True)


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Nayak AI")
        self.geometry("650x700")

        def on_closing():
            if messagebox.askokcancel("Quit", "Do you want to quit?"):
                # speak("thanks for using me")
                app.destroy()

        self.protocol("WM_DELETE_WINDOW", on_closing)

        def addEmailKey():
            def save():
                email = sender_email.get()
                emailkey = email_key.get()

                if email == "" or emailkey == "":
                    messagebox.showerror("Error", "Please fill in all fields.")
                    return

                # Regular expression for email format validation
                email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

                if not re.match(email_regex, email):
                    messagebox.showerror("Error", "Invalid email format.")
                    return

                conn = sqlite3.connect('users.db')
                cursor = conn.cursor()
                cursor.execute(
                    "CREATE TABLE IF NOT EXISTS email (uid	INTEGER NOT NULL,email_address	TEXT NOT NULL UNIQUE,email_key	TEXT NOT NULL UNIQUE,FOREIGN KEY(uid) REFERENCES users(id));")

                # Check if the email already exists
                cursor.execute("SELECT * FROM email WHERE email_address=?", (email,))
                if cursor.fetchone():
                    messagebox.showerror("Error", "Email already exists.")
                    conn.close()
                    return

                cursor.execute("SELECT id from users WHERE email = ?", (email,))
                if cursor.fetchone():
                    cursor.execute("SELECT id from users WHERE email = ?", (email,))
                    uidtuple = cursor.fetchone()
                    uid = uidtuple[0]
                    cursor.execute("INSERT INTO email (uid, email_address, email_key) VALUES (?, ?, ?)",
                                   (uid, email, emailkey))
                    conn.commit()
                    conn.close()
                    add_email_frmae.place_forget()
                else:
                    messagebox.showerror("Email error", "Please enter your email and email key.")

            add_email_frmae = customtkinter.CTkFrame(app, border_width=1, border_color="white", corner_radius=10)
            add_email_frmae.place(x=250, y=30)
            sender_email = customtkinter.CTkEntry(add_email_frmae, placeholder_text="Email")
            sender_email.place(relx=0.15, rely=0.10)
            email_key = customtkinter.CTkEntry(add_email_frmae, placeholder_text="Email Key")
            email_key.place(relx=0.15, rely=0.25)
            save_data = customtkinter.CTkButton(add_email_frmae, text="Save", command=save)
            save_data.place(relx=0.15, rely=0.45)
            exit_button = customtkinter.CTkButton(add_email_frmae, text="exit", command=add_email_frmae.place_forget)
            exit_button.place(relx=0.15, rely=0.65)

        def addEmailAddresses():
            def save():
                id = user_id.get()
                name = reciever_name.get()
                email = receiver_email_address.get()

                if id == "" or name == "" or email == "":
                    messagebox.showerror("Error", "Please fill in all fields.")
                    return
                # Regular expression for email format validation
                email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

                if not re.match(email_regex, email):
                    messagebox.showerror("Error", "Invalid email format.")
                    return

                conn = sqlite3.connect('users.db')
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM  users WHERE id=?", (id,))
                if cursor.fetchone():
                    cursor.execute(
                        "CREATE TABLE IF NOT EXISTS receiver (uid	INTEGER NOT NULL,receiver_name	TEXT NOT NULL UNIQUE,receiver_email	TEXT NOT NULL UNIQUE,FOREIGN KEY(uid) REFERENCES users(id));")

                    # Check if the email already exists
                    cursor.execute("SELECT * FROM receiver WHERE receiver_email=?", (email,))
                    if cursor.fetchone():
                        messagebox.showerror("Error", "Email already exists.")
                        conn.close()
                        return

                    try:
                        cursor.execute("INSERT INTO receiver (uid, receiver_name, receiver_email) VALUES (?, ?, ?)",
                                       (id, name, email))
                        conn.commit()
                        conn.close()
                        addemailframe.place_forget()
                    except sqlite3.Error as e:
                        messagebox.showerror("SQLite Error", "e")
                else:
                    messagebox.showerror("Error", "Invalid ID")
                    return

            addemailframe = customtkinter.CTkFrame(app, border_width=1, border_color="white", corner_radius=10)
            addemailframe.place(x=250, y=30)
            user_id = customtkinter.CTkEntry(addemailframe, placeholder_text="ID")
            user_id.place(relx=0.15, rely=0.10)
            reciever_name = customtkinter.CTkEntry(addemailframe, placeholder_text="Name")
            reciever_name.place(relx=0.15, rely=0.25)
            receiver_email_address = customtkinter.CTkEntry(addemailframe, placeholder_text="Email Address")
            receiver_email_address.place(relx=0.15, rely=0.40)
            save_data = customtkinter.CTkButton(addemailframe, text="Save", command=save)
            save_data.place(relx=0.15, rely=0.65)

            exit_button = customtkinter.CTkButton(addemailframe, text="exit", command=addemailframe.place_forget)
            exit_button.place(relx=0.15, rely=0.80)

        def addWhatsAppNomber():
            def save():
                id = user_id.get()
                name = reciever_name.get()
                number = receiver_mobile_number.get()

                if id == "" or name == "" or number == "":
                    messagebox.showerror("Error", "Please fill in all fields.")
                    return

                def is_valid_indian_mobile_number(mobile_number):
                    # Regular expression to match a 10-digit number starting with +91
                    pattern = r'^\+91\d{10}$'
                    if re.match(pattern, mobile_number):
                        return True
                    else:
                        return False

                if is_valid_indian_mobile_number(number):
                    conn = sqlite3.connect('users.db')
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM  users WHERE id=?", (id,))
                    if cursor.fetchone():
                        cursor.execute(
                            "CREATE TABLE IF NOT EXISTS whatsapp (uid	INTEGER NOT NULL,receiver_name	TEXT NOT NULL UNIQUE,receiver_mobile_number	TEXT NOT NULL UNIQUE,FOREIGN KEY(uid) REFERENCES users(id));")

                        # Check if the email already exists
                        cursor.execute("SELECT * FROM  whatsapp WHERE receiver_mobile_number=?", (number,))
                        if cursor.fetchone():
                            messagebox.showerror("Error", "number already exists.")
                            conn.close()
                            return

                        cursor.execute(
                            "INSERT INTO whatsapp (uid, receiver_name, receiver_mobile_number) VALUES (?, ?, ?)",
                            (id, name, number))
                        conn.commit()
                        conn.close()
                        addwhatsappnomber.place_forget()
                    else:
                        messagebox.showerror("Error", "Invalid ID")
                        return
                else:
                    messagebox.showerror("Validation Error", "Invalid number format")
                    return

                addwhatsappnomber.place_forget()

            addwhatsappnomber = customtkinter.CTkFrame(app, border_width=1, border_color="white", corner_radius=10)
            addwhatsappnomber.place(x=250, y=30)
            user_id = customtkinter.CTkEntry(addwhatsappnomber, placeholder_text="ID")
            user_id.place(relx=0.15, rely=0.10)
            reciever_name = customtkinter.CTkEntry(addwhatsappnomber, placeholder_text="Name")
            reciever_name.place(relx=0.15, rely=0.25)
            receiver_mobile_number = customtkinter.CTkEntry(addwhatsappnomber, placeholder_text="+91 0000 0000")
            receiver_mobile_number.place(relx=0.15, rely=0.40)
            save_data = customtkinter.CTkButton(addwhatsappnomber, text="Save", command=save)
            save_data.place(relx=0.15, rely=0.65)
            exit_button = customtkinter.CTkButton(addwhatsappnomber, text="exit",
                                                  command=addwhatsappnomber.place_forget)
            exit_button.place(relx=0.15, rely=0.80)

        def addOpenAIAPIKEY():
            def save():
                id = user_id.get()
                apikey = api_key.get()

                if id == "" or apikey == "":
                    messagebox.showerror("Error", "Please fill in all fields.")
                    return

                conn = sqlite3.connect('users.db')
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM  users WHERE id=?", (id,))
                if cursor.fetchone():
                    cursor.execute(
                        "CREATE TABLE IF NOT EXISTS apikey (uid	INTEGER NOT NULL,api_key	TEXT NOT NULL UNIQUE,FOREIGN KEY(uid) REFERENCES users(id));")

                    cursor.execute("INSERT INTO apikey (uid, api_key) VALUES (?, ?)",
                                   (id, apikey))
                    conn.commit()
                    conn.close()
                else:
                    messagebox.showerror("Error", "Invalid ID")
                    return

                addapikey.place_forget()

            addapikey = customtkinter.CTkFrame(app, border_width=1, border_color="white", corner_radius=10)
            addapikey.place(x=250, y=30)
            user_id = customtkinter.CTkEntry(addapikey, placeholder_text="ID")
            user_id.place(relx=0.15, rely=0.10)
            api_key = customtkinter.CTkEntry(addapikey, placeholder_text="Open AI Key")
            api_key.place(relx=0.15, rely=0.25)
            save_data = customtkinter.CTkButton(addapikey, text="Save", command=save)
            save_data.place(relx=0.15, rely=0.50)
            exit_button = customtkinter.CTkButton(addapikey, text="exit", command=addapikey.place_forget)
            exit_button.place(relx=0.15, rely=0.65)

        menu = CTkTitleMenu(self, padx=1, width=50)
        button_1 = menu.add_cascade("File")
        button_2 = menu.add_cascade("Edit")
        button_3 = menu.add_cascade("Settings")
        button_4 = menu.add_cascade("About")

        dropdown1 = CustomDropdownMenu(widget=button_1)
        dropdown1.add_option(option="Open")
        dropdown1.add_option(option="Save")

        dropdown1.add_separator()

        sub_menu = dropdown1.add_submenu("Export As")
        sub_menu.add_option(option=".TXT")
        sub_menu.add_option(option=".PDF")

        dropdown2 = CustomDropdownMenu(widget=button_2)
        dropdown2.add_option(option="Cut")
        dropdown2.add_option(option="Copy")
        dropdown2.add_option(option="Paste")

        dropdown3 = CustomDropdownMenu(widget=button_3)
        dropdown3.add_separator()

        sub_menu = dropdown3.add_submenu("Email")
        sub_menu.add_option(option="Email Key", command=addEmailKey)
        sub_menu.add_option(option="Add Email", command=addEmailAddresses)

        dropdown3.add_option(option="Add Number", command=addWhatsAppNomber)

        dropdown3.add_option(option="Add API key", command=addOpenAIAPIKEY)
        dropdown3.add_option(option="Add Image")

        dropdown4 = CustomDropdownMenu(widget=button_4)
        dropdown4.add_option(option="Hello World")

        self.main_frame = MainFrame(self)
        self.main_frame.pack(fill="both", padx=1, pady=1, expand=True)


if __name__ == "__main__":
    app = App()
    app.mainloop()

