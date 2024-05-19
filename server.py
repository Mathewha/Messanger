import threading
import socket
import hashlib


class Server:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind(('192.168.0.112', 8001)) # put the local ip address
        self.clients = {}
        self.client_threads = {}

    def hash_password(self, password):
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def listening(self):
        self.s.listen(5)
        print('Server started. Waiting for connections...')
        while True:
            conn, addr = self.s.accept()
            threading.Thread(target=self.handle_client, args=(conn, addr)).start()

    def handle_client(self, conn, addr):
        try:
            login_info = conn.recv(1024).decode('utf-8')
            if '+' not in login_info:
                conn.sendall("Invalid login format".encode('utf-8'))
                conn.close()
                return

            name, password = login_info.split('+')
            hashed_password = self.hash_password(password)

            # For demonstration, assume the password is 'password'
            if hashed_password != self.hash_password('password'):
                conn.sendall("Authentication failed".encode('utf-8'))
                conn.close()
                return

            self.clients[name] = conn
            self.client_threads[conn] = threading.Thread(target=self.sending_and_receiving, args=(conn, addr, name))
            self.client_threads[conn].start()
            print(f"New connection from {addr} as {name}")
        except Exception as e:
            print(f"Error handling client {addr}: {e}")
            conn.close()

    def sending_and_receiving(self, conn, addr, name):
        try:
            while True:
                data = conn.recv(1024).decode('utf-8')
                if not data:
                    break
                if '|' not in data:
                    conn.sendall("Invalid message format".encode('utf-8'))
                    continue

                mes, user, sender = data.split('|')
                if user in self.clients:
                    self.clients[user].sendall(mes.encode('utf-8'))
                else:
                    conn.sendall("User not found".encode('utf-8'))
        except ConnectionResetError:
            print(f"Connection with {addr} closed.")
        except Exception as e:
            print(f"Error in communication with {addr}: {e}")
        finally:
            self.cleanup_client(conn, name)

    def cleanup_client(self, conn, name):
        if name in self.clients:
            del self.clients[name]
        if conn in self.client_threads:
            self.client_threads[conn].join()
            del self.client_threads[conn]
        conn.close()
        print(f"Client {name} disconnected")


if __name__ == "__main__":
    server = Server()
    server.listening()
