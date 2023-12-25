from socket import *
import threading
import sys
import logging
from DAO.database_access import DatabaseAccess
from Service.password import Password
from Service.color_utils import colored_print
import colorama
class TCPServer(threading.Thread):
    '''
    This class is used to process the client's messages.
    '''

    def __init__(self, user_ip, user_port, tcp_socket, server_ip, server_port):
        '''
        Initializes the class.
        '''
        threading.Thread.__init__(self)
        self.user_ip = user_ip
        self.user_port = user_port
        self.tcp_socket = tcp_socket
        self.username = None
        self.isOnline = True
        self.DatabaseAccess = DatabaseAccess()
        self.server_ip = server_ip
        self.server_port = server_port
        self.active_chat_rooms = set()
        colored_print("New thread started for " + user_ip + ":" + str(user_port), "success")

    def run(self) :
        '''
        This method is called when the thread is created.
        '''

        self.lock = threading.Lock()
        colored_print("Connection from : " + self.user_ip + ":" + str(self.user_port), "success")
        while True:
            try:
                message = self.tcp_socket.recv(1024).decode().split()
                logging.info("Received message: " + str(message) + " from " + self.user_ip + ":" + str(self.user_port))
                if str(message[0]).lower() == "create-room":
                    self.create_chat_room(message[1])
                elif str(message[0]).lower() == "join-room":
                    self.join_chat_room(message[1])
                elif str(message[0]).lower() == "create":
                    if self.DatabaseAccess.user_exists(str(message[1])):
                        response = "create-failed-user-exists"
                        colored_print("From " + self.user_ip + ":" + str(self.user_port) + " : " + response, "error")
                        logging.info("Sent message: " + response + " to " + self.user_ip + ":" + str(self.user_port))
                        self.tcp_socket.send(response.encode())
                    else:
                        salt = Password.generate_salt()
                        self.DatabaseAccess.create_user(str(message[1]), Password.hash(str(message[2]), salt), salt)
                        response = "create-success"
                        colored_print("From " + self.user_ip + ":" + str(self.user_port) + " : " + response, "success")
                        logging.info("Sent message: " + response + " to " + self.user_ip + ":" + str(self.user_port))
                        self.tcp_socket.send(response.encode())
                elif str(message[0]).lower() == "login":
                    if self.DatabaseAccess.user_exists(str(message[1])):
                        salt = self.DatabaseAccess.get_user_salt(str(message[1]))
                        if Password.verify(self.DatabaseAccess.get_password(str(message[1])), str(message[2]), salt):
                            if self.DatabaseAccess.is_user_online(str(message[1])):
                                response = "login-failed-already-logged-in"
                                colored_print("From " + self.user_ip + ":" + str(self.user_port) + " : " + response, "error")
                                logging.info("Sent message: " + response + " to " + self.user_ip + ":" + str(self.user_port))
                                self.tcp_socket.send(response.encode())
                            else:
                                self.DatabaseAccess.set_user_online(str(message[1]), self.user_port, self.user_ip)
                                self.username = str(message[1])
                                self.lock.acquire()
                                try:
                                    pass
                                finally:
                                    self.lock.release()
                                response = "login-success"
                                colored_print("From " + self.user_ip + ":" + str(self.user_port) + " : " + response, "success")
                                logging.info("Sent message: " + response + " to " + self.user_ip + ":" + str(self.user_port))
                                self.tcp_socket.send(response.encode())
                        else:
                            response = "login-failed-incorrect-password"
                            colored_print("From " + self.user_ip + ":" + str(self.user_port) + " : " + response, "error")
                            logging.info("Sent message: " + response + " to " + self.user_ip + ":" + str(self.user_port))
                            self.tcp_socket.send(response.encode())
                    else:
                        response = "login-failed-username-not-found"
                        colored_print("From " + self.user_ip + ":" + str(self.user_port) + " : " + response, "error")
                        logging.info("Sent message: " + response + " to " + self.user_ip + ":" + str(self.user_port))
                        self.tcp_socket.send(response.encode())

                elif str(message[0]).lower() == "log-out":
                    if self.DatabaseAccess.user_exists(str(message[1])):
                        if self.DatabaseAccess.is_user_online(str(message[1])):
                            self.DatabaseAccess.set_user_offline(str(message[1]))
                            self.lock.acquire()
                            try:
                                pass
                            finally:
                                self.lock.release()
                            response = "log-out-success " + str(message[1])
                            colored_print("From " + self.user_ip + ":" + str(self.user_port) + " : " + response, "success")
                            logging.info("Sent message: " + response + " to " + self.user_ip + ":" + str(self.user_port))
                            self.tcp_socket.send(response.encode())
                            self.tcp_socket.close()
                        else:
                            response = "logout-failed-not-logged-in"
                            colored_print("From " + self.user_ip + ":" + str(self.user_port) + " : " + response, "error")
                            logging.info("Sent message: " + response + " to " + self.user_ip + ":" + str(self.user_port))
                            self.tcp_socket.send(response.encode())
                    else:
                        response = "log-out-fail-incorrect-username"
                        colored_print("From " + self.user_ip + ":" + str(self.user_port) + " : " + response, "error")
                        logging.info("Sent message: " + response + " to " + self.user_ip + ":" + str(self.user_port))
                        self.tcp_socket.send(response.encode())
            except OSError as e:
                colored_print("Connection closed by " + self.user_ip + ":" + str(self.user_port), "error")
                logging.error("Error: " + str(e))
                break

    def create_chat_room(self, room_name):
        if room_name not in self.active_chat_rooms:
            self.active_chat_rooms.add(room_name)
            response = "create-room-success"
        else:
            response = "create-room-failed"
        colored_print("From " + self.user_ip + ":" + str(self.user_port) + " : " + response, "info")
        logging.info("Sent message: " + response + " to " + self.user_ip + ":" + str(self.user_port))
        self.tcp_socket.send(response.encode())

    def join_chat_room(self, room_name):
        if room_name in self.active_chat_rooms:
            response = "join-room-success"
        else:
            response = "join-room-failed"
        colored_print("From " + self.user_ip + ":" + str(self.user_port) + " : " + response, "info")
        logging.info("Sent message: " + response + " to " + self.user_ip + ":" + str(self.user_port))
        self.tcp_socket.send(response.encode())

    def send_p2p_info(self):
        p2p_info = f"p2p {self.server_ip}:{self.server_port}"
        self.tcp_socket.send(p2p_info.encode())


colorama.init()
colored_print("Starting server...", "success")
logging.basicConfig(filename="server.log", level=logging.INFO)
port = 15600
# databaseAccess = DatabaseAccess()
hostname = gethostname()
try:
    host = gethostbyname(hostname)
except gaierror:
    colored_print("Error: Hostname could not be resolved.", "error")
    logging.error("Error: Hostname could not be resolved.")
    sys.exit()

colored_print("Server IP address: " + host, "success")
colored_print("Server port: " + str(port), "success")
tcp_server_socket = socket(AF_INET, SOCK_STREAM)
# tcp_server_socket.close()
tcp_server_socket.bind((host, port))
tcp_server_socket.listen(5)

while True:
    try:
        connection_socket, addr = tcp_server_socket.accept()
        new_thread = TCPServer(addr[0], addr[1], connection_socket, host, port)
        new_thread.start()
        new_thread.send_p2p_info()
    except KeyboardInterrupt:
        colored_print("Server stopped.", "error")
        logging.info("Server stopped.")
        break
tcp_server_socket.close()
