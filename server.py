import threading
import socket
import logging

class Processor:
    def __init__(self):
        self.clients = {}

    def add_client(self, name, conn):
        self.clients[name] = conn

    def process_login_info(self, login_info):
        if not isinstance(login_info, str) or ' ' in login_info.strip():
            raise ValueError("Invalid login information format. Login info must be a single word.")
        return login_info.strip()

    def process_message(self, data):
        try:
            mes, user, sender = data.split('|')
            return mes, user, sender
        except ValueError:
            raise ValueError("Invalid message format")

    def send_message(self, mes, user):
        if user in self.clients:
            self.clients[user].sendall(mes.encode('utf-8'))
            return True
        else:
            return False

class Server:
    def __init__(self):
        log_format = '%(process)d|%(threadName)s|%(levelname)s|%(message)s'
        logging.basicConfig(level=logging.DEBUG,
                            format=log_format,
                            handlers=[
                                logging.FileHandler('messenger_server.txt', 'w'),
                                logging.StreamHandler()
                            ])
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        while True:
            try:
                port = input("Set Port: ")
                port = int(port)
                break
            except Exception as e:
                logging.error(f"Wrong format of the port: {e}")

        logging.info(f"Server information: IP: {socket.gethostbyname(socket.gethostname())}, Port: {port}")
        self.s.bind(('', port))
        self.processor = Processor()

    def listening(self):
        self.s.listen(5)
        logging.info('Server started. Waiting for connections...')
        while True:
            try:
                conn, addr = self.s.accept()
                login_info = conn.recv(1024).decode('utf-8')
                name = self.processor.process_login_info(login_info)
                self.processor.add_client(name, conn)
                threading.Thread(target=self.sending_and_receiving, args=(conn, addr, name)).start()
            except Exception as e:
                logging.error(f"Error during accepting connection: {e}")

    def sending_and_receiving(self, conn, addr, name):
        logging.info(f"New connection from {addr} - Username: {name}")
        while True:
            try:
                data = conn.recv(1024).decode('utf-8')
                logging.info(f"Received from {addr}: {data}")
                if not data:
                    logging.info(f"No data received. Closing connection with {addr}")
                    break
                mes, user, sender = self.processor.process_message(data)
                if not self.processor.send_message(mes, user):
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

if __name__ == "__main__":
    server = Server()
    server.listening()
