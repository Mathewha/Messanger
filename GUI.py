import tkinter as tk
from tkinter import messagebox
from tkinter import ttk


class Client:
    def __init__(self):
        pass

    def connect(self, server_address):
        # Connect to the server
        pass

    def select_user(self, user_id):
        # Select a user to communicate with
        pass

    def send_message(self, user_id, message):
        pass

    def receive_message(self):
        pass


class GUI:
    # will utilize the rest of the attributes when we get to the server part,
    # since we don't know what to expect from the interaction between our approach of the GUI
    # and the server. (this includes the unfinished receive_message part)
    def __init__(self, login_info, user_info, chat_history):
        self.root = tk.Tk()
        self.root.title("ChatApp")
        self.login_info = login_info
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        # base of the chatapp windows

        self.login_page()

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
        self.username_entry.bind('<Return>', lambda event: self.login())  # Changed
        self.password_entry.bind('<Return>', lambda event: self.login())  # Changed
        # redirection to login

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if username == self.login_info['username'] and password == self.login_info['password']:
            self.notebook.forget(self.login_frame)
            self.user_chat_window()
            # redirection to chat window (inserting users)

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
        self.username_entry.bind('<Return>', lambda event: self.start_chat())  # Changed
        # redirection to text chat

    def start_chat(self):
        username = self.username_entry.get().strip()
        if username:
            chat_frame = ttk.Frame(self.notebook)
            self.notebook.add(chat_frame, text=username)
            self.inside_chat(chat_frame, username)
            self.notebook.select(chat_frame)
        else:
            messagebox.showerror("Error", "Please enter a username to start chat")
        return username

    def inside_chat(self, chat_frame, user):
        frame = chat_frame
        # borrowing frame

        chat_text = tk.Text(frame, state=tk.DISABLED)
        chat_text.pack(expand=True, fill=tk.BOTH)

        message_entry = tk.Entry(frame)
        message_entry.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        send_button = tk.Button(frame, text="Send", command=lambda: self.send_message(message_entry, chat_text, user))
        # redirection to sending message
        send_button.pack(side=tk.BOTTOM)
        message_entry.bind('<Return>', lambda event: self.send_message(message_entry, chat_text, user))  # Changed

    # WILL ADD SENDING TO ANOTHER USER ONCE SERVER WORKS
    def send_message(self, message_entry, chat_text, user):
        message = message_entry.get()
        if message:
            chat_text.config(state=tk.NORMAL)
            chat_text.insert(tk.END, f"You: {message}\n")
            chat_text.config(state=tk.DISABLED)
            message_entry.delete(0, tk.END)
        return message_entry, user  # Changed
        # text information for the server (message and for what user it is)

    # WILL ADD IT ONCE SERVER WORKS
    def receive_message(self):
        pass

    # MAYBE IN THE FUTURE (TOO COMPLICATED FOR NOW)
    def current_status(self):
        # of user
        pass

    def friends_list(self):

        pass

    def online_user_list(self):

        pass


if __name__ == "__main__":
    login_info = {'username': 'a', 'password': 'a'}
    app = GUI(login_info, 'a', 'a')
