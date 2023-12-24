from socket import *
import threading
import time
import sys
import logging
import select
from Service.color_utils import colored_print
import colorama

class Client(threading.Thread):
    def __init__(self):
        super().__init__()
        colored_print("Enter the server IP address: ", "prompt")
        self.serverIpAddress = input()
        self.serverPort = 15600
        self.clientSocket = socket(AF_INET, SOCK_STREAM)
        self.clientSocket.connect((self.serverIpAddress, self.serverPort))
        self.loginCredentials = (None, None)  # (username, password) for client login
        self.isOnline = False
        self.clientServerPort = None

        logging.basicConfig(filename='client.log', filemode='w', level=logging.INFO)

        userSelection = None

        while userSelection != "3":
            colored_print("1. Create account", "menu")
            colored_print("2. Login", "menu")
            colored_print("3. Logout", "menu")
            colored_print("Enter your choice: ", "prompt")
            userSelection = input()

            if userSelection == "1":
                self.create_account()
            elif userSelection == "2" and not self.isOnline:
                status = self.login()
                clientServerPort = int(self.get_open_port())
                if status:
                    self.isOnline = True
                    self.clientServerPort = clientServerPort
            elif userSelection == "3" and self.isOnline:
                self.logout()
                self.isOnline = False
                self.loginCredentials = (None, None)
                self.clientServerPort = None
                self.clientSocket.close()
                colored_print("Logged out successfully.", "success")
            else:
                colored_print("Invalid choice.", "error")



    def create_account(self):
        '''
        This method is used to create a new account.
        '''
        colored_print("Enter username: ", "prompt")
        username = input()
        colored_print("Enter password: ", "prompt")
        password = input()
        self.clientSocket.send(("create " + username + " " + password).encode())
        response = self.clientSocket.recv(1024).decode()
        logging.info("Received message: " + response + " from " + self.serverIpAddress + ":" + str(self.serverPort))
        if response == "create-success":
            colored_print("Account created successfully.", "success")
        elif response == "create-failed-user-exists":
            colored_print("Account creation failed. Username already exists.", "error")

    def login(self):
        '''
        This method is used to login to an existing account.
        '''
        colored_print("Enter username: ", "prompt")
        username = input()
        colored_print("Enter password: ", "prompt")
        password = input()
        self.clientSocket.send(("login " + username + " " + password).encode())
        response = self.clientSocket.recv(1024).decode()
        logging.info("Received message: " + response + " from " + self.serverIpAddress + ":" + str(self.serverPort))
        if response == "login-success":
            self.loginCredentials = (username, password)
            colored_print("Login successful.", "success")
            return True
        elif response == "login-failed-already-logged-in":
            colored_print("Login failed. User is already logged in.", "error")
            return False
        elif response == "login-failed-incorrect-password":
            colored_print("Login failed. Wrong password.", "error")
            return False
        elif response == "login-failed-username-not-found":
            colored_print("Login failed. Wrong username.", "error")
            return False

    def logout(self):
        '''
        This method is used to log-out of an existing account.
        '''
        username = str(self.loginCredentials[0])
        colored_print(username, "prompt")
        self.clientSocket.send(("log-out " + username).encode())
        response = self.clientSocket.recv(1024).decode()
        logging.info("Received message: " + response + " from " + self.serverIpAddress + ":" + str(self.serverPort))
        if response == "log-out-success":
            colored_print("Logout successful.", "success")
        elif response == "logout-failed-not-logged-in":
            colored_print("Logout failed. User is not logged in.", "error")
        elif response == "logout-failed-incorrect-username":
            colored_print("Logout failed. Wrong username.", "error")



    def get_open_port(self):
        '''
        This method is used to get an open port on the client machine.
        '''
        s = socket(AF_INET, SOCK_STREAM)
        s.bind(("", 0))
        s.listen(1)
        port = s.getsockname()[1]
        s.close()
        return port


colorama.init()
main = Client() # create a client object
