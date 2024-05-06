from openai import OpenAI
import sqlite3
from tkinter import messagebox

def ai(prompt, id, model="gpt-3.5-turbo"):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT api_key FROM  apikey WHERE uid=?", (id,))
    if cursor.fetchone():
        cursor.execute("SELECT api_key FROM  apikey WHERE uid=?", (id,))
        apikey = cursor.fetchone()
        api_key = apikey[0]
        client = OpenAI(api_key=api_key)
        f"OpenAI Response for prompt:{prompt} \n *****************\n\n"
        messages = [{"role": "user", "content": prompt}]
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=1,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )

        response = response.choices[0].message.content
        cursor.execute("CREATE TABLE IF NOT EXISTS openai (uid	INTEGER NOT NULL,prompts	TEXT NOT NULL,responses	TEXT NOT NULL,FOREIGN KEY(uid) REFERENCES users(id));")
        cursor.execute("INSERT INTO openai (uid, prompts, responses) VALUES (?, ?, ?)",
                       (id, prompt, response))
        conn.commit()
        conn.close()



        return response
    else:
        cursor.close()
        messagebox.showerror("Exception", "Please try again")


