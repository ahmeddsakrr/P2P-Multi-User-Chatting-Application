from socket import *
import threading
import time
import sys
import logging
from DAO.database_access import DatabaseAccess
from Service.password import Password
from Service.color_utils import colored_print
class TCPServer(threading.Thread):
    '''
    This class is used to process the client's messages.
    '''

    def __init__(self, user_ip, user_port, tcp_socket):
        '''
        Initializes the class.
        '''
        threading.Thread.__init__(self)
        self.user_ip = user_ip
        self.user_port = user_port
        self.tcp_socket = tcp_socket
        self.username = None
        self.isOnline = True
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
                    if str(message[0]).lower() == "create":
                        if DatabaseAccess.user_exists(str(message[1])):
                            response = "create-failed-user-exists"
                            colored_print("From " + self.user_ip + ":" + str(self.user_port) + " : " + response, "error")
                            logging.info("Sent message: " + response + " to " + self.user_ip + ":" + str(self.user_port))
                            self.tcp_socket.send(response.encode())
                        else:
                            salt = Password.generate_salt()
                            DatabaseAccess.create_user(str(message[1]), Password.hash(str(message[2]), salt))
                            response = "create-success"
                            colored_print("From " + self.user_ip + ":" + str(self.user_port) + " : " + response, "success")
                            logging.info("Sent message: " + response + " to " + self.user_ip + ":" + str(self.user_port))
                            self.tcp_socket.send(response.encode())
                    elif str(message[0]).lower() == "login":
                        if DatabaseAccess.user_exists(str(message[1])):
                            if Password.verify(DatabaseAccess.get_password(str(message[1])), str(message[2])):
                                if DatabaseAccess.is_user_online(str(message[1])):
                                    response = "login-failed-already-logged-in"
                                    colored_print("From " + self.user_ip + ":" + str(self.user_port) + " : " + response, "error")
                                    logging.info("Sent message: " + response + " to " + self.user_ip + ":" + str(self.user_port))
                                    self.tcp_socket.send(response.encode())
                                else:
                                    DatabaseAccess.set_user_online(str(message[1]), self.user_port, self.user_ip)
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
                        if DatabaseAccess.user_exists(str(message[1])):
                            if DatabaseAccess.is_user_online(str(message[1])):
                                DatabaseAccess.set_user_offline(str(message[1]))
                                self.lock.acquire()
                                try:
                                    pass
                                finally:
                                    self.lock.release()
                                response = "log-out-success" + str(message[1])
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


colored_print("Starting server...", "success")
logging.basicConfig(filename="server.log", level=logging.INFO)
port = 15600
databaseAccess = DatabaseAccess()
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
tcp_server_socket.bind((host, port))
tcp_server_socket.listen(5)

while True:
    try:
        connection_socket, addr = tcp_server_socket.accept()
        new_thread = TCPServer(addr[0], addr[1], connection_socket)
        new_thread.start()
    except KeyboardInterrupt:
        colored_print("Server stopped.", "error")
        logging.info("Server stopped.")
        break
tcp_server_socket.close()