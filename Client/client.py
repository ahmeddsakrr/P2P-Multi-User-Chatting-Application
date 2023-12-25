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
        self.peerIp = None
        self.peerPort = None

        logging.basicConfig(filename='client.log', filemode='w', level=logging.INFO)

        userSelection = None

        while userSelection != "4":
            colored_print("1. Chat Menu", "menu")
            colored_print("2. Manage Account", "menu")
            colored_print("3. Logout", "menu")
            colored_print("4. Exit", "menu")
            colored_print("Enter your choice: ", "prompt")
            userSelection = input()

            if userSelection == "1":
                self.chat_menu()
            elif userSelection == "2" and not self.isOnline:
                status = self.login()
                clientServerPort = int(self.get_open_port())
                if status:
                    self.isOnline = True
                    self.clientServerPort = int(self.get_open_port())
                    self.establish_p2p_connection()
            elif userSelection == "3" and self.isOnline:
                self.logout()
                self.isOnline = False
                self.loginCredentials = (None, None)
                self.clientServerPort = None
                self.clientSocket.close()
                colored_print("Logged out successfully.", "success")
            elif userSelection == "4":
                self.exit_program()
            else:
                colored_print("Invalid choice.", "error")

    def chat_menu(self):
            while True:
                colored_print("1. Create Chat Room", "menu")
                colored_print("2. Join Chat Room", "menu")
                colored_print("3. Back to Main Menu", "menu")
                colored_print("Enter your choice: ", "prompt")
                choice = input()

                if choice == "1":
                    self.create_chat_room()
                elif choice == "2":
                    self.join_chat_room()
                elif choice == "3":
                    break
                else:
                    colored_print("Invalid choice.", "error")

    def create_chat_room(self):
            colored_print("Enter chat room name: ", "prompt")
            room_name = input()
            self.clientSocket.send(f"create-room {room_name}".encode())
            response = self.clientSocket.recv(1024).decode()
            logging.info("Received message: " + response + " from " + self.serverIpAddress + ":" + str(self.serverPort))
            if response == "create-room-success":
                colored_print(f"Chat room '{room_name}' created successfully.", "success")
            elif response == "create-room-failed":
                colored_print(f"Failed to create chat room '{room_name}'.", "error")

    def join_chat_room(self):
            colored_print("Enter chat room name: ", "prompt")
            room_name = input()
            self.clientSocket.send(f"join-room {room_name}".encode())
            response = self.clientSocket.recv(1024).decode()
            logging.info("Received message: " + response + " from " + self.serverIpAddress + ":" + str(self.serverPort))
            if response == "join-room-success":
                colored_print(f"Joined chat room '{room_name}' successfully.", "success")
                # Additional logic for handling chat in the room can be added here
            elif response == "join-room-failed":
                colored_print(f"Failed to join chat room '{room_name}'.", "error")



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

    def establish_p2p_connection(self):
        self.clientSocket.send(f"p2p {self.clientServerPort}".encode())
        p2p_info = self.clientSocket.recv(1024).decode()
        self.peerIp, self.peerPort = self.parse_p2p_info(p2p_info)
        colored_print(f"Peer-to-peer connection established with {self.peerIp}:{self.peerPort}", "success")
        # Now you can start a new thread to handle peer-to-peer communication

    def parse_p2p_info(self, info):
        parts = info.split()
        if len(parts) == 2 and parts[0].lower() == "p2p":
            ip, port = parts[1].split(":")
            return ip, int(port)
        return None, None

    def exit_program(self):
        self.clientSocket.send("exit".encode())
        sys.exit()


colorama.init()
main = Client() # create a client object
