import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import socket
import threading

# THINGS TO IMPROVE IN THE FUTURE:


# Not allowing user to make multiple instances of the same chat
# Registering page (right now we need to manually change the variables)
# Remembering the previous chat history
# Remembering previous chat users, friends list
# A way to leave the app without forcing the closure of the program (we haven't utilized the client.disconnect in any way nor we don't have a quit button)
# Make the app accessible even if it's not connected (now it just doesn't appear when there is no connection to the server)
# Maybe better UI?

# TO TEST:

# Multiple chats with multiple clients at the same time (we don't have the resources to test that, it was only tested with 2 clients for now)



class Client:
    def __init__(self, host, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host  # the address and port are given as attribute given from class GUI
        self.port = port

    def connect(self):
        self.s.connect((self.host, self.port))

    def send_message(self, mess, user, sender):
        messinfo = f"{mess}|{user}|{sender}"
        self.s.send(messinfo.encode('utf-8'))

    def send_login(self, username, password):
        login_info = f"{username}+{password}"
        self.s.send(login_info.encode('utf-8'))

    def receive_message(self):
        while True:
            data = self.s.recv(1024).decode('utf-8')
            if not data:
                break
            return data

    def disconnect(self):
        self.s.close()

class GUI:
    def __init__(self, login_info):
        self.root = tk.Tk()
        self.root.title("ChatApp")
        self.login_info = login_info
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.client = Client('192.168.0.112', 8001)  # Update the IP address to your server's IP
        self.client.connect()

        self.login_page()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def login_page(self):
        self.login_frame = tk.Frame(self.notebook)
        self.notebook.add(self.login_frame, text="Login")

        self.username_label = tk.Label(self.login_frame, text="Username:")
        self.username_label.pack()
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.pack()
        self.password_label = tk.Label(self.login_frame, text="Password:")
        self.password_label.pack()
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.pack()

        self.login_button = tk.Button(self.login_frame, text="Login", command=self.login)
        self.login_button.pack()
        self.username_entry.bind('<Return>', lambda event: self.login())
        self.password_entry.bind('<Return>', lambda event: self.login())

    def login(self):
        self.username = self.username_entry.get()
        self.password = self.password_entry.get()
        if self.username == self.login_info['username'] and self.password == self.login_info['password']:
            self.client.send_login(self.username, self.password)
            self.notebook.forget(self.login_frame)
            self.user_chat_window()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def user_chat_window(self):
        self.user_selection_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.user_selection_frame, text="Select User")

        self.user_label = tk.Label(self.user_selection_frame, text="Enter Username:")
        self.user_label.pack()

        self.username_entry = tk.Entry(self.user_selection_frame)
        self.username_entry.pack()

        self.start_chat_button = tk.Button(self.user_selection_frame, text="Start Chat", command=self.start_chat)
        self.start_chat_button.pack()
        self.username_entry.bind('<Return>', lambda event: self.start_chat())

    def start_chat(self):
        username = self.username_entry.get().strip()
        if username:
            chat_frame = ttk.Frame(self.notebook)
            self.notebook.add(chat_frame, text=username)
            self.inside_chat(chat_frame, username)
            self.notebook.select(chat_frame)
        else:
            messagebox.showerror("Error", "Please enter a username to start chat")

    def inside_chat(self, chat_frame, user):
        chat_text = tk.Text(chat_frame, state=tk.DISABLED)
        chat_text.pack(expand=True, fill=tk.BOTH)

        message_entry = tk.Entry(chat_frame)
        message_entry.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        send_button = tk.Button(chat_frame, text="Send", command=lambda: self.send_message(message_entry, chat_text, user))
        send_button.pack(side=tk.BOTTOM)
        message_entry.bind('<Return>', lambda event: self.send_message(message_entry, chat_text, user))
        threading.Thread(target=self.receive_message, args=(chat_text, user)).start()

    def send_message(self, message_entry, chat_text, user):
        message = message_entry.get()
        if message:
            chat_text.config(state=tk.NORMAL)
            chat_text.insert(tk.END, f"You: {message}\n")
            chat_text.config(state=tk.DISABLED)
            message_entry.delete(0, tk.END)
            self.client.send_message(message, user, self.username)

    def receive_message(self, chat_text, user):
        while True:
            message = self.client.receive_message()
            if message:
                chat_text.config(state=tk.NORMAL)
                chat_text.insert(tk.END, f"{user}: {message}\n")
                chat_text.config(state=tk.DISABLED)

# proper client disconnection handling with a window close
    def on_closing(self):
        self.client.disconnect()
        self.root.destroy()

if __name__ == "__main__":
    login_info = {'username': 'a', 'password': 'a'}
    app = GUI(login_info)
