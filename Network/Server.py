from socket import *
import threading
import sys
import logging

import select

from DAO.database_access import DatabaseAccess
from Service.password import Password
from Service.color_utils import colored_print
import colorama
class Server(threading.Thread):
    '''
    This class is used to process the client's messages.
    '''

    def __init__(self, user_ip, user_port, tcp_socket, server_ip, server_port):
        '''
        Initializes the class.
        '''
        threading.Thread.__init__(self)
        self.peer_ip = user_ip
        self.peer_port = user_port
        self.tcp_socket = tcp_socket
        self.username = None
        self.isOnline = True
        self.DatabaseAccess = DatabaseAccess()
        self.udp_server = None
        self.server_ip = server_ip
        self.server_port = server_port
        self.active_chat_rooms = set()
        colored_print("New thread started for " + user_ip + ":" + str(user_port), "success")

    def run(self) :
        '''
        This method is called when the thread is created.
        '''

        self.lock = threading.Lock()
        colored_print("Connection from : " + self.peer_ip + ":" + str(self.peer_port), "success")
        while True:
            try:
                message = self.tcp_socket.recv(1024).decode().split()
                if not message:
                    colored_print("No message received", "error")
                    break
                logging.info("Received message: " + str(message) + " from " + self.peer_ip + ":" + str(self.peer_port))
                if str(message[0]).lower() == "create-room":
                    self.create_chat_room(message[1])
                elif str(message[0]).lower() == "join-room":
                    self.join_chat_room(message[1])
                elif str(message[0]).lower() == "create":
                    if self.DatabaseAccess.user_exists(str(message[1])):
                        response = "create-failed-user-exists"
                        colored_print("From " + self.peer_ip + ":" + str(self.peer_port) + " : " + response, "error")
                        logging.info("Sent message: " + response + " to " + self.peer_ip + ":" + str(self.peer_port))
                        self.tcp_socket.send(response.encode())
                    else:
                        salt = Password.generate_salt()
                        self.DatabaseAccess.create_user(str(message[1]), Password.hash(str(message[2]), salt), salt)
                        response = "create-success"
                        colored_print("From " + self.peer_ip + ":" + str(self.peer_port) + " : " + response, "success")
                        logging.info("Sent message: " + response + " to " + self.peer_ip + ":" + str(self.peer_port))
                        self.tcp_socket.send(response.encode())
                elif str(message[0]).lower() == "login":
                    if self.DatabaseAccess.user_exists(str(message[1])):
                        salt = self.DatabaseAccess.get_user_salt(str(message[1]))
                        if Password.verify(self.DatabaseAccess.get_password(str(message[1])), str(message[2]), salt):
                            if self.DatabaseAccess.is_user_online(str(message[1])):
                                response = "login-failed-already-logged-in"
                                colored_print("From " + self.peer_ip + ":" + str(self.peer_port) + " : " + response, "error")
                                logging.info("Sent message: " + response + " to " + self.peer_ip + ":" + str(self.peer_port))
                                self.tcp_socket.send(response.encode())
                            else:
                                self.DatabaseAccess.set_user_online(str(message[1]), self.peer_port, self.peer_ip)
                                self.username = str(message[1])
                                self.lock.acquire()
                                try:
                                    tcp_threads[self.username] = self
                                finally:
                                    self.lock.release()
                                response = "login-success"
                                colored_print("From " + self.peer_ip + ":" + str(self.peer_port) + " : " + response, "success")
                                logging.info("Sent message: " + response + " to " + self.peer_ip + ":" + str(self.peer_port))
                                self.tcp_socket.send(response.encode())
                        else:
                            response = "login-failed-incorrect-password"
                            colored_print("From " + self.peer_ip + ":" + str(self.peer_port) + " : " + response, "error")
                            logging.info("Sent message: " + response + " to " + self.peer_ip + ":" + str(self.peer_port))
                            self.tcp_socket.send(response.encode())
                    else:
                        response = "login-failed-username-not-found"
                        colored_print("From " + self.peer_ip + ":" + str(self.peer_port) + " : " + response, "error")
                        logging.info("Sent message: " + response + " to " + self.peer_ip + ":" + str(self.peer_port))
                        self.tcp_socket.send(response.encode())

                elif str(message[0]).lower() == "log-out":
                    if self.DatabaseAccess.user_exists(str(message[1])):
                        if self.DatabaseAccess.is_user_online(str(message[1])):
                            self.DatabaseAccess.set_user_offline(str(message[1]))
                            self.lock.acquire()
                            try:
                                if message[1] in tcp_threads:
                                    del tcp_threads[message[1]]
                            finally:
                                self.lock.release()
                            response = "log-out-success " + str(message[1])
                            colored_print("From " + self.peer_ip + ":" + str(self.peer_port) + " : " + response, "success")
                            logging.info("Sent message: " + response + " to " + self.peer_ip + ":" + str(self.peer_port))
                            self.tcp_socket.send(response.encode())
                            self.tcp_socket.close()
                            self.udp_server.timer.cancel()
                            break
                        else:
                            response = "logout-failed-not-logged-in"
                            colored_print("From " + self.peer_ip + ":" + str(self.peer_port) + " : " + response, "error")
                            logging.info("Sent message: " + response + " to " + self.peer_ip + ":" + str(self.peer_port))
                            self.tcp_socket.send(response.encode())
                    else:
                        response = "log-out-fail-incorrect-username"
                        colored_print("From " + self.peer_ip + ":" + str(self.peer_port) + " : " + response, "error")
                        logging.info("Sent message: " + response + " to " + self.peer_ip + ":" + str(self.peer_port))
                        self.tcp_socket.send(response.encode())
                elif str(message[0]).lower() == "search":
                    if self.DatabaseAccess.user_exists(str(message[1])):
                        if self.DatabaseAccess.is_user_online(str(message[1])):
                            response = "search-success " + str(message[1]) + " " + str(self.DatabaseAccess.get_user_ip(str(message[1]))) + " " + str(self.DatabaseAccess.get_user_port(str(message[1])))
                            colored_print("From " + self.peer_ip + ":" + str(self.peer_port) + " : " + response, "success")
                            logging.info("Sent message: " + response + " to " + self.peer_ip + ":" + str(self.peer_port))
                            self.tcp_socket.send(response.encode())
                        else:
                            response = "search-failed-not-logged-in"
                            colored_print("From " + self.peer_ip + ":" + str(self.peer_port) + " : " + response, "error")
                            logging.info("Sent message: " + response + " to " + self.peer_ip + ":" + str(self.peer_port))
                            self.tcp_socket.send(response.encode())
                    else:
                        response = "search-failed-incorrect-username"
                        colored_print("From " + self.peer_ip + ":" + str(self.peer_port) + " : " + response, "error")
                        logging.info("Sent message: " + response + " to " + self.peer_ip + ":" + str(self.peer_port))
                        self.tcp_socket.send(response.encode())
                elif str(message[0]).lower() == "create-room":
                    if self.DatabaseAccess.chat_room_exists(str(message[1])):
                        response = "create-room-failed"
                        colored_print("From " + self.peer_ip + ":" + str(self.peer_port) + " : " + response, "error")
                        logging.info("Sent message: " + response + " to " + self.peer_ip + ":" + str(self.peer_port))
                        self.tcp_socket.send(response.encode())
                    else:
                        self.DatabaseAccess.create_chat_room(str(message[1]))
                        response = "create-room-success"
                        colored_print("From " + self.peer_ip + ":" + str(self.peer_port) + " : " + response, "success")
                        logging.info("Sent message: " + response + " to " + self.peer_ip + ":" + str(self.peer_port))
                        self.tcp_socket.send(response.encode())
                elif str(message[0]).lower() == "join-room":
                    if self.DatabaseAccess.chat_room_exists(str(message[1])):
                        id, peers = self.DatabaseAccess.get_chat_room_peers(str(message[1]))
                        peers.append(message[2])
                        peers = list(set(peers)) # remove duplicates
                        self.DatabaseAccess.update_chat_room_peers(id, peers)
                        response = "join-room-success"
                        colored_print("From " + self.peer_ip + ":" + str(self.peer_port) + " : " + response, "success")
                        logging.info("Sent message: " + response + " to " + self.peer_ip + ":" + str(self.peer_port))
                        self.tcp_socket.send(response.encode())
                    else:
                        response = "join-room-failed"
                        colored_print("From " + self.peer_ip + ":" + str(self.peer_port) + " : " + response, "error")
                        logging.info("Sent message: " + response + " to " + self.peer_ip + ":" + str(self.peer_port))
                        self.tcp_socket.send(response.encode())

                elif str(message[0]).lower() == "exit":
                    self.DatabaseAccess.remove_user_from_room(message[1], message[2])
                    response = "exit-success"

            except OSError as e:
                colored_print("Connection closed by " + self.peer_ip + ":" + str(self.peer_port), "error")
                logging.error("Error: " + str(e))
                break

    def create_chat_room(self, room_name):
        if room_name not in self.active_chat_rooms:
            self.active_chat_rooms.add(room_name)
            response = "create-room-success"
        else:
            response = "create-room-failed"
        colored_print("From " + self.peer_ip + ":" + str(self.peer_port) + " : " + response, "info")
        logging.info("Sent message: " + response + " to " + self.peer_ip + ":" + str(self.peer_port))
        self.tcp_socket.send(response.encode())

    def join_chat_room(self, room_name):
        if room_name in self.active_chat_rooms:
            response = "join-room-success"
        else:
            response = "join-room-failed"
        colored_print("From " + self.peer_ip + ":" + str(self.peer_port) + " : " + response, "info")
        logging.info("Sent message: " + response + " to " + self.peer_ip + ":" + str(self.peer_port))
        self.tcp_socket.send(response.encode())

    def send_p2p_info(self):
        p2p_info = f"p2p {self.server_ip}:{self.server_port}"
        self.tcp_socket.send(p2p_info.encode())

class UDPServer(threading.Thread):

    def __int__(self, username, clientSocket):
        threading.Thread.__init__(self)
        self.timer = threading.Timer(3, self.waitHelloMessage)
        self.tcp_socket = clientSocket
        self.username = username
        self.DatabaseAccess = DatabaseAccess()

    def waitHelloMessage(self):
        if self.username is not None:
            self.DatabaseAccess.set_user_offline(self.username)
            if self.username in tcp_threads:
                del tcp_threads[self.username]
            self.tcp_socket.close()
            colored_print("Removed " + self.username + " from online peers", "error")

    def reset_timer(self):
        self.timer.cancel()
        self.timer = threading.Timer(3, self.waitHelloMessage)
        self.timer.start()




colorama.init()
colored_print("Starting server...", "success")
logging.basicConfig(filename="server.log", level=logging.INFO)
port = 15600
udp_port = 15500
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
tcp_server_socket.bind((host, port))
tcp_server_socket.listen(5)
udp_socket = socket(AF_INET, SOCK_DGRAM)
udp_socket.bind((host, udp_port))

tcp_threads = {}
online_users = {}
accounts = {}

inputs = [tcp_server_socket, udp_socket]

while True:
    try:
        colored_print("Waiting for connection...", "success")
        readable, writable, exceptions = select.select(inputs, [], [])
        for s in readable:
            if s is tcp_server_socket:
                connection_socket, addr = tcp_server_socket.accept()
                new_thread = Server(addr[0], addr[1], connection_socket, host, port)
                new_thread.start()
                # new_thread.send_p2p_info()
            elif s is udp_socket:
                message, address = s.recvfrom(1024)
                message = message.decode().split()
                if message[0] == "hello":
                    if message[1] in tcp_threads:
                        tcp_threads[message[1]].reset_timer()
                        colored_print("Received hello message from " + message[1], "success")
                        logging.info("Received hello message from " + message[1])
        # connection_socket, addr = tcp_server_socket.accept()
        # new_thread = Server(addr[0], addr[1], connection_socket, host, port)
        # new_thread.start()
        # new_thread.send_p2p_info()
    except KeyboardInterrupt:
        colored_print("Server stopped.", "error")
        logging.info("Server stopped.")
        break
tcp_server_socket.close()
