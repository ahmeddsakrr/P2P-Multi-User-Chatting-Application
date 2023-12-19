from socket import *
import threading
import time
import sys
import logging
from DAO.database_access import DatabaseAccess
from password import Password
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
        print("New thread started for " + user_ip + ":" + str(user_port))

        def run(self) :
            '''
            This method is called when the thread is created.
            '''

            self.lock = threading.Lock()
            print("Connection from : " + user_ip + ":" + str(user_port))
            while True:
                try:
                    message = self.tcp_socket.recv(1024).decode().split()
                    logging.info("Received message: " + str(message) + " from " + self.user_ip + ":" + str(self.user_port))
                    if str(message[0]).lower() == "create":
                        if DatabaseAccess.user_exists(str(message[1])):
                            response = "create-failed-user-exists"
                            print("From " + self.user_ip + ":" + str(self.user_port) + " : " + response)
                            logging.info("Sent message: " + response + " to " + self.user_ip + ":" + str(self.user_port))
                            self.tcp_socket.send(response.encode())
                        else:
                            salt = Password.generate_salt()
                            DatabaseAccess.create_user(str(message[1]), Password.hash(str(message[2]), salt))
                            response = "create-success"
                            print("From " + self.user_ip + ":" + str(self.user_port) + " : " + response)
                            logging.info("Sent message: " + response + " to " + self.user_ip + ":" + str(self.user_port))
                            self.tcp_socket.send(response.encode())
                    elif str(message[0]).lower() == "login":
                        if DatabaseAccess.user_exists(str(message[1])):
                            if Password.verify(DatabaseAccess.get_password(str(message[1])), str(message[2])):
                                if DatabaseAccess.is_user_online(str(message[1])):
                                    response = "login-failed-already-logged-in"
                                    print("From " + self.user_ip + ":" + str(self.user_port) + " : " + response)
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
                                    print("From " + self.user_ip + ":" + str(self.user_port) + " : " + response)
                                    logging.info("Sent message: " + response + " to " + self.user_ip + ":" + str(self.user_port))
                                    self.tcp_socket.send(response.encode())
                            else:
                                response = "login-failed-incorrect-password"
                                print("From " + self.user_ip + ":" + str(self.user_port) + " : " + response)
                                logging.info("Sent message: " + response + " to " + self.user_ip + ":" + str(self.user_port))
                                self.tcp_socket.send(response.encode())
                        else:
                            response = "login-failed-username-not-found"
                            print("From " + self.user_ip + ":" + str(self.user_port) + " : " + response)
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
                                print("From " + self.user_ip + ":" + str(self.user_port) + " : " + response)
                                logging.info("Sent message: " + response + " to " + self.user_ip + ":" + str(self.user_port))
                                self.tcp_socket.send(response.encode())
                                self.tcp_socket.close()
                            else:
                                response = "logout-failed-not-logged-in"
                                print("From " + self.user_ip + ":" + str(self.user_port) + " : " + response)
                                logging.info("Sent message: " + response + " to " + self.user_ip + ":" + str(self.user_port))
                                self.tcp_socket.send(response.encode())
                        else:
                            response = "log-out-fail-incorrect-username"
                            print("From " + self.user_ip + ":" + str(self.user_port) + " : " + response)
                            logging.info("Sent message: " + response + " to " + self.user_ip + ":" + str(self.user_port))
                            self.tcp_socket.send(response.encode())
                except OSError as e:
                    print("Error: " + str(e))
                    logging.error("Error: " + str(e))
                    break
