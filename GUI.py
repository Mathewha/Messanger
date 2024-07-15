import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import socket
import threading


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

    def send_login(self, username):
        login_info = f"{username}"
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
            self.login_page()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid IP address and port number")
        except socket.error as e:
            messagebox.showerror("Connection Failed", f"Failed to connect to {ip_address}:{port}\nError: {e}")

    def login_page(self):
        self.login_frame = tk.Frame(self.notebook)
        self.notebook.add(self.login_frame, text="Login")

        self.username_label = tk.Label(self.login_frame, text="Username:")
        self.username_label.pack()
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.pack()

        self.login_button = tk.Button(self.login_frame, text="Login", command=self.check_login)
        self.login_button.pack()
        self.username_entry.bind('<Return>', lambda event: self.check_login())

    def check_login(self):
        self.username = self.username_entry.get()
        if not isinstance(self.username, str) or ' ' in self.username.strip() or not self.username.strip():
            messagebox.showerror("Login Failed", "Invalid username.")
        else:
            self.client.send_login(self.username)
            self.notebook.forget(self.login_frame)
            self.user_chat_window()


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
