import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import socket
import threading

class Client:
    def __init__(self, host, port):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port

    def connect(self):
        self.s.connect((self.host, self.port))

    def send_message(self, mess, user, sender):
        messinfo = f"{mess}|{user}|{sender}"
        self.s.send(messinfo.encode('utf-8'))

    def send_login(self, username, password):
        login_info = f"LOGIN+{username}+{password}"
        self.s.send(login_info.encode('utf-8'))

    def send_registration(self, username, password):
        registration_info = f"REGISTER+{username}+{password}"
        self.s.send(registration_info.encode('utf-8'))

    def receive_message(self):
        while True:
            data = self.s.recv(1024).decode('utf-8')
            if not data:
                break
            return data

    def disconnect(self):
        self.s.close()

class GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ChatApp")
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.conversations = []

        self.connection_page()
        self.root.mainloop()

    def connection_page(self):
        self.connection_frame = tk.Frame(self.notebook)
        self.notebook.add(self.connection_frame, text="Connect")

        self.ip_label = tk.Label(self.connection_frame, text="IP Address:")
        self.ip_label.pack()
        self.ip_entry = tk.Entry(self.connection_frame)
        self.ip_entry.pack()

        self.port_label = tk.Label(self.connection_frame, text="Port:")
        self.port_label.pack()
        self.port_entry = tk.Entry(self.connection_frame)
        self.port_entry.pack()

        self.connect_button = tk.Button(self.connection_frame, text="Connect", command=self.check_connection)
        self.connect_button.pack()
        self.ip_entry.bind('<Return>', lambda event: self.check_connection())
        self.port_entry.bind('<Return>', lambda event: self.check_connection())

    def check_connection(self):
        ip_address = self.ip_entry.get()
        port = self.port_entry.get()
        try:
            port = int(port)
            if not (0 <= port <= 65535):
                raise ValueError("Port out of range")

            self.client = Client(ip_address, port)
            self.client.connect()

            messagebox.showinfo("Connection Successful", f"Connected to {ip_address}:{port}")
            self.notebook.forget(self.connection_frame)
            self.sign_in_sign_up_page()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid IP address and port number")
        except socket.error as e:
            messagebox.showerror("Connection Failed", f"Failed to connect to {ip_address}:{port}\nError: {e}")

    def sign_in_sign_up_page(self):
        self.sign_in_sign_up_frame = tk.Frame(self.notebook)
        self.notebook.add(self.sign_in_sign_up_frame, text="Sign In / Sign Up")

        self.sign_in_label = tk.Label(self.sign_in_sign_up_frame, text="Sign In", font=("Arial", 18), fg="blue", cursor="hand2")
        self.sign_in_label.pack(pady=20)
        self.sign_in_label.bind("<Button-1>", lambda e: self.login_page())

        self.sign_up_label = tk.Label(self.sign_in_sign_up_frame, text="Sign Up", font=("Arial", 18), fg="blue", cursor="hand2")
        self.sign_up_label.pack(pady=20)
        self.sign_up_label.bind("<Button-1>", lambda e: self.register_page())

    def register_page(self):
        self.register_frame = tk.Frame(self.notebook)
        self.notebook.add(self.register_frame, text="Register")

        self.new_username_label = tk.Label(self.register_frame, text="New Username:")
        self.new_username_label.pack()
        self.new_username_entry = tk.Entry(self.register_frame)
        self.new_username_entry.pack()
        self.new_password_label = tk.Label(self.register_frame, text="New Password:")
        self.new_password_label.pack()
        self.new_password_entry = tk.Entry(self.register_frame, show="*")
        self.new_password_entry.pack()

        self.register_button = tk.Button(self.register_frame, text="Register", command=self.register)
        self.register_button.pack()
        self.new_username_entry.bind('<Return>', lambda event: self.register())
        self.new_password_entry.bind('<Return>', lambda event: self.register())

    def register(self):
        new_username = self.new_username_entry.get()
        new_password = self.new_password_entry.get()
        self.client.send_registration(new_username, new_password)
        response = self.client.receive_message()
        if response == "Registration successful":
            messagebox.showinfo("Registration Successful", "You can now log in with your new credentials")
            self.notebook.forget(self.register_frame)
            self.login_page()
        elif response == "Username already taken":
            messagebox.showerror("Registration Failed", "Username already taken. Please choose another one.")
        else:
            messagebox.showerror("Registration Failed", "An error occurred during registration.")

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

        self.login_button = tk.Button(self.login_frame, text="Login", command=self.check_login)
        self.login_button.pack()
        self.username_entry.bind('<Return>', lambda event: self.check_login())
        self.password_entry.bind('<Return>', lambda event: self.check_login())

    def check_login(self):
        self.username = self.username_entry.get()
        self.password = self.password_entry.get()
        self.client.send_login(self.username, self.password)
        response = self.client.receive_message()
        if response == "Login successful":
            messagebox.showinfo("Login Successful", "You are now logged in")
            self.notebook.forget(self.login_frame)
            self.notebook.forget(self.sign_in_sign_up_frame)
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
            if username in self.conversations:
                messagebox.showerror("Error", "This conversation already exists")
            else:
                self.conversations.append(username)
                chat_frame = ttk.Frame(self.notebook)
                self.notebook.add(chat_frame, text=username)
                self.inside_chat(chat_frame, username)
                self.notebook.select(chat_frame)
        else:
            messagebox.showerror("Error", "Please enter a username to start chat")
        return username

    def inside_chat(self, chat_frame, user):
        chat_text = tk.Text(chat_frame, state=tk.DISABLED)
        chat_text.pack(expand=True, fill=tk.BOTH)

        message_entry = tk.Entry(chat_frame)
        message_entry.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        send_button = tk.Button(chat_frame, text="Send",
                                command=lambda: self.send_message(message_entry, chat_text, user))
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

    def on_closing(self):
        self.client.disconnect()
        self.root.destroy()

app = GUI()
