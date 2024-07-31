import threading
import socket
import logging
import json

class Server:
    def __init__(self):
        log_format = '%(process)d|%(threadName)s|%(levelname)s|%(message)s'
        logging.basicConfig(level=logging.DEBUG,
                            format=log_format,
                            handlers=[
                                logging.FileHandler('messenger_server.log', 'w'),
                                logging.StreamHandler()
                            ])
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        port = input("Set Port: ")
        port = int(port)
        logging.info(f"Server information: IP: {socket.gethostbyname(socket.gethostname())}, Port: {port}")
        self.s.bind(('', port))
        self.clients = {}
        self.load_credentials()  # Load user credentials from file

    def load_credentials(self):
        try:
            with open('credentials.json', 'r') as f:
                self.credentials = json.load(f)
                logging.info("Loaded credentials from credentials.json")
        except FileNotFoundError:
            self.credentials = {}
            logging.warning("credentials.json not found, starting with an empty credentials dictionary")
        except Exception as e:
            self.credentials = {}
            logging.error(f"Error loading credentials: {e}")

    def save_credentials(self):
        try:
            with open('credentials.json', 'w') as f:
                json.dump(self.credentials, f)
                logging.info("Saved credentials to credentials.json")
        except Exception as e:
            logging.error(f"Error saving credentials: {e}")

    def listening(self):
        self.s.listen(5)
        logging.info('Server started. Waiting for connections...')
        while True:
            try:
                conn, addr = self.s.accept()
                threading.Thread(target=self.handle_client, args=(conn, addr)).start()
            except Exception as e:
                logging.error(f"Error during accepting connection: {e}")

    def handle_client(self, conn, addr):
        while True:
            try:
                data = conn.recv(1024).decode('utf-8')
                if data.startswith("REGISTER"):
                    _, username, password = data.split('+')
                    if username not in self.credentials:
                        self.credentials[username] = password
                        self.save_credentials()
                        conn.sendall("Registration successful".encode('utf-8'))
                        logging.info(f"New user registered: {username}")
                    else:
                        conn.sendall("Username already taken".encode('utf-8'))
                        logging.warning(f"Registration failed: Username {username} already taken")
                elif data.startswith("LOGIN"):
                    _, username, password = data.split('+')
                    if username in self.credentials and self.credentials[username] == password:
                        self.clients[username] = conn
                        conn.sendall("Login successful".encode('utf-8'))
                        threading.Thread(target=self.sending_and_receiving, args=(conn, addr, username)).start()
                        break
                    else:
                        conn.sendall("Invalid username or password".encode('utf-8'))
                        logging.warning(f"Login failed for username: {username}")
            except Exception as e:
                logging.error(f"Error during handling client: {e}")
                break

    def sending_and_receiving(self, conn, addr, username):
        logging.info(f"New connection from {addr} - Username: {username}")
        while True:
            try:
                data = conn.recv(1024).decode('utf-8')
                logging.info(f"Received from {addr}: {data}")
                if not data:
                    logging.info(f"No data received. Closing connection with {addr}")
                    break
                mes, user, sender = data.split('|')
                logging.info(f"Clients: {self.clients}")
                if user in self.clients:
                    self.clients[user].sendall(mes.encode('utf-8'))
                    logging.debug(f"Sent message to {user}")
                else:
                    conn.sendall("User not found".encode('utf-8'))
                    logging.warning(f"User {user} not found")
            except ConnectionResetError:
                logging.error(f"Connection with {addr} closed")
                break
            except Exception as e:
                logging.error(f"Error during sending/receiving data: {e}")
                break
        conn.close()
        logging.info(f"Connection with {addr} closed")

server = Server()
server.listening()
