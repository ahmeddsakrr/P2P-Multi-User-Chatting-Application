from socket import *
import threading
import time
import sys
import logging
import select
from Service.color_utils import colored_print, colored_print_no_newline
import colorama
from Network.PeerServer import PeerServer
from Network.PeerClient import PeerClient

class Client(threading.Thread):
    def __init__(self):
        super().__init__()
        # colored_print("Enter the server IP address: ", "prompt")
        # colored_print("Enter the server IP address: ", "prompt")
        host = gethostname()
        self.serverIpAddress = gethostbyname(host)
        self.serverPort = 15600
        self.clientSocket = socket(AF_INET, SOCK_STREAM)
        self.clientSocket.connect((self.serverIpAddress, self.serverPort))
        self.udpSocket = socket(AF_INET, SOCK_DGRAM)
        self.udpPort = 15500
        self.loginCredentials = (None, None)  # (username, password) for client login
        self.isOnline = False
        self.clientServerPort = None
        self.roomServerPort = None
        self.peerServer = None
        self.peerClient = None
        self.timer = None
        #############################################
        self.peerIp = None
        self.peerPort = None

        logging.basicConfig(filename='client.log', filemode='w', level=logging.INFO)

        userSelection = None

        # while userSelection != "4":
        #     colored_print("1. Chat Menu", "menu")
        #     colored_print("2. Manage Account", "menu")
        #     colored_print("3. Logout", "menu")
        #     colored_print("4. Exit", "menu")
        #     colored_print("Enter your choice: ", "prompt")
        #     userSelection = input()
        while userSelection != "3":
            colored_print("1. Create Account", "menu")
            colored_print("2. Login", "menu")
            colored_print("3. Logout", "menu")
            colored_print("4. Search for user", "menu")
            colored_print("5. Create private chat", "menu")
            colored_print("6. Create chat room", "menu")
            colored_print("7. Join chat room", "menu")
            colored_print_no_newline("Enter your choice: ", "prompt")
            userSelection = input()

            if userSelection == "1":
                self.create_account()
            elif userSelection == "2" and not self.isOnline:
                status = self.login()
                clientServerPort = int(self.get_open_port())
                roomServerPort = int(self.get_open_port())
                if status:
                    self.isOnline = True
                    self.clientServerPort = clientServerPort
                    self.roomServerPort = roomServerPort
                    # self.establish_p2p_connection()
                    if self.loginCredentials[0] is not None:
                        self.peerServer = PeerServer(self.loginCredentials[0], self.clientServerPort, self.roomServerPort)
                        self.peerServer.start()
                        self.sendHelloMessage()

            elif userSelection == "3" and self.isOnline:
                try:
                    self.logout()
                    self.isOnline = False
                    self.loginCredentials = (None, None)
                    self.peerServer.isOnline = False
                    self.peerServer.tcp_server_socket.close()
                    if self.peerClient is not None:
                        self.peerClient.tcp_socket.close()

                    # self.clientServerPort = None
                    # self.clientSocket.close()
                    colored_print("Logged out successfully.", "success")
                except error as e:
                    logging.info("Error: " + str(e))
            elif userSelection == "4":
                # self.exit_program()
                colored_print_no_newline("Enter username to search: ", "prompt")
                username_to_search = input()
                search_status = self.search_user(username_to_search)
                if search_status is not None and search_status:
                    colored_print("User found.", "success")
                    colored_print("IP address of the user: " + username_to_search + "is " + search_status, "success")
            elif userSelection == "5" and self.isOnline:
                colored_print("Enter username of the user you want to chat with: ", "prompt")
                username = input()
                search_status = self.search_user(username)
                if search_status is not None and search_status:
                    colored_print("User found.", "success")
                    search_status = search_status.split(":")
                    self.peerServer.chat = 1
                    self.peerClient = PeerClient(connected_ip=search_status[0], connected_port=int(search_status[1]), username=self.loginCredentials[0], peer_server=self.peerServer, received_response=None, choice="5", room_id=None, room_peers = None)
                    self.peerClient.start()
                    self.peerClient.join()
            elif userSelection == "6" and self.isOnline:
                colored_print("Enter room id: ", "prompt")
                room_id = input()
                self.create_chat_room(room_id)
                colored_print("Chat room created successfully.", "success")
            elif userSelection == "7" and self.isOnline:
                colored_print("Enter room id: ", "prompt")
                room_id = input()
                join_status = self.join_chat_room(room_id)
                if join_status is not None and join_status:
                    ip_to_connect = "192.168.1.5"
                    self.peerServer.room = 1
                    self.peerClient = PeerClient(ip_to_connect, None, self.loginCredentials[0], self.peerServer, None, "7", room_id, join_status)
                    self.peerClient.start()
                    self.peerClient.join()
            elif userSelection == "accept-connection" and self.isOnline:
                accept_message = "accept-connection" + " " + str(self.loginCredentials[0])
                logging.info("Sent message: " + accept_message + " to " + str(self.peerIp) + ":" + str(self.peerPort))
                self.peerServer.connected_peer_socket.send(accept_message.encode())
                self.peerClient = PeerClient(self.peerServer.connected_peer_ip, self.peerServer.connected_peer_port, self.loginCredentials[0], self.peerServer, "accept-connection", "5", None, None)
                self.peerClient.start()
                self.peerClient.join()
            elif userSelection == "reject-connection" and self.isOnline:
                self.peerServer.connected_peer_socket.send("reject-connection".encode())
                self.peerServer.isChatting = False
                logging.info("Sent message: " + "reject-connection" + " to " + str(self.peerIp) + ":" + str(self.peerPort))
            elif userSelection == "cancel":
                self.timer.cancel()
            else:
                colored_print("Invalid choice.", "error")
        if userSelection == "cancel":
            self.clientSocket.close()


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

    def create_chat_room(self, room_name):
        self.clientSocket.send(f"create-room {room_name}".encode())
        logging.info("Sent message: " + "create-room " + room_name + " to " + self.serverIpAddress + ":" + str(self.serverPort))
        response = self.clientSocket.recv(1024).decode()
        logging.info("Received message: " + response + " from " + self.serverIpAddress + ":" + str(self.serverPort))
        if response == "create-room-success":
            colored_print(f"Chat room '{room_name}' created successfully.", "success")
        elif response == "create-room-failed":
            colored_print(f"Failed to create chat room '{room_name}'.", "error")

    def join_chat_room(self,room_name):
        message = "join-room " + room_name + " " + str(self.roomServerPort)
        logging.info("Sent message: " + message + " to " + self.serverIpAddress + ":" + str(self.serverPort))
        self.clientSocket.send(message.encode())
        response = self.clientSocket.recv(1024).decode()
        logging.info("Received message: " + response + " from " + self.serverIpAddress + ":" + str(self.serverPort))
        peers_list_start = response.index("[")
        peers_list_end = response.index("]") + 1
        peers_list = response[peers_list_start:peers_list_end]
        peers_list = eval(peers_list)
        response = response.split()
        if response[0] == "join-room-success":
            colored_print(f"Joined chat room '{room_name}' successfully.", "success")
            return peers_list
            # Additional logic for handling chat in the room can be added here
        elif response == "join-room-failed":
            colored_print(f"Failed to join chat room '{room_name}'.", "error")
            return 0



    def create_account(self):
        '''
        This method is used to create a new account.
        '''
        colored_print_no_newline("Enter username: ", "prompt")
        username = input()
        colored_print_no_newline("Enter password: ", "prompt")
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
        colored_print_no_newline("Enter username: ", "prompt")
        username = input()
        colored_print_no_newline("Enter password: ", "prompt")
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
        # colored_print(username, "prompt")
        self.clientSocket.send(("log-out " + username).encode())
        response = self.clientSocket.recv(1024).decode()
        logging.info("Received message: " + response + " from " + self.serverIpAddress + ":" + str(self.serverPort))
        if response == "log-out-success":
            colored_print("Logout successful.", "success")
            self.timer.cancel()
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

    def sendHelloMessage(self):
        if self.loginCredentials[0] is not None:
            message = "hello " + str(self.loginCredentials[0])
            logging.info("Sent message: " + message + " to " + self.serverIpAddress + ":" + str(self.udpPort))
            self.udpSocket.sendto(message.encode(), (self.serverIpAddress, self.udpPort))
            self.timer = threading.Timer(1, self.sendHelloMessage)
            self.timer.start()

    def search_user(self, username):
        logging.info("Sent message: " + "search " + username + " to " + self.serverIpAddress + ":" + str(self.serverPort))
        self.clientSocket.send(("search " + username).encode())
        response = self.clientSocket.recv(1024).decode()
        logging.info("Received message: " + response + " from " + self.serverIpAddress + ":" + str(self.serverPort))
        response = response.split()
        if response[0] == "search-failed":
            colored_print("Search failed. User not found.", "error")
            return None
        elif response == "search-success":
            colored_print("Search successful.", "success")
            return response[1]


colorama.init()
main = Client() # create a client object
