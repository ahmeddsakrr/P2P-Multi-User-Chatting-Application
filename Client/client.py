from socket import *
import threading
import time
import sys
import logging
import select


class Client(threading.Thread):
    def __init__(self):
        super().__init__()
        self.serverIpAddress = input("Enter server IP address: ")
        self.serverPort = 15600
        self.clientSocket = socket(AF_INET, SOCK_STREAM)
        self.clientSocket.connect((self.serverIpAddress, self.serverPort))
        self.loginCredentials = (None, None)  # (username, password) for client login
        self.isOnline = False
        self.clientServerPort = None

        logging.basicConfig(filename='client.log', filemode='w', level=logging.INFO)

        userSelection = None

        while userSelection != "3":

            print("1. Create account")
            print("2. Login")
            print("3. Logout")
            userSelection = input("Enter your choice: ")

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
                print("Logged out successfully.")
            else:
                print("Invalid choice.")



    def create_account(self):
        '''
        This method is used to create a new account.
        '''
        username = input("Enter username: ")
        password = input("Enter password: ")
        self.clientSocket.send(("create " + username + " " + password).encode())
        response = self.clientSocket.recv(1024).decode()
        logging.info("Received message: " + response + " from " + self.serverIpAddress + ":" + str(self.serverPort))
        if response == "create-success":
            print("Account created successfully.")
        elif response == "create-failed-user-exists":
            print("Account creation failed. Username already exists.")

    def login(self):
        '''
        This method is used to login to an existing account.
        '''
        username = input("Enter username: ")
        password = input("Enter password: ")
        self.clientSocket.send(("login " + username + " " + password).encode())
        response = self.clientSocket.recv(1024).decode()
        logging.info("Received message: " + response + " from " + self.serverIpAddress + ":" + str(self.serverPort))
        if response == "login-success":
            print("Login successful.")
            return True
        elif response == "login-failed-already-logged-in":
            print("Login failed. User is already logged in.")
            return False
        elif response == "login-failed-incorrect-password":
            print("Login failed. Wrong password.")
            return False
        elif response == "login-failed-username-not-found":
            print("Login failed. Wrong username.")
            return False

    def logout(self):
        '''
        This method is used to log-out of an existing account.
        '''
        username = str(self.loginCredentials[0])
        self.clientSocket.send(("log-out " + username).encode())
        response = self.clientSocket.recv(1024).decode()
        logging.info("Received message: " + response + " from " + self.serverIpAddress + ":" + str(self.serverPort))
        if response == "log-out-success":
            print("Logout successful.")
        elif response == "logout-failed-not-logged-in":
            print("Logout failed. User is not logged in.")
        elif response == "logout-failed-incorrect-username":
            print("Logout failed. Wrong username.")



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


main = Client() # create a client object
