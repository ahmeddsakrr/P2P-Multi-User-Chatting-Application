from socket import *
import logging
import threading
import select

from Service.color_utils import colored_print
from Service.password import Password
from DAO.database_access import DatabaseAccess
import colorama


class PeerServer(threading.Thread):
    '''
    This class is used to process the server side of the peer-to-peer connection.
    '''

    def __init__(self, username, peer_server_port, chat_room_server_port):
        '''
        Peer Server Initialization
        '''
        threading.Thread.__init__(self)
        self.peer_server_hostname = None
        self.username = username
        self.peer_server_port = peer_server_port
        self.chat_room_server_port = chat_room_server_port
        self.tcp_server_socket = socket(AF_INET, SOCK_STREAM)
        self.udp_server_socket = socket(AF_INET, SOCK_DGRAM)

        self.isChatting = False # Flag to check if the user is chatting
        self.isOnline = True # Flag to check if the user is online

        self.connected_peer_ip = None # IP address of the connected peer
        self.connected_peer_port = None # Port number of the connected peer
        self.connected_peer_socket = None # Socket of the connected peer
        self.connected_peer_username = None
        self.chat = 0
        self.room = 0

    def run(self) -> None:

        colored_print("Peer server started", "success")

        hostname = gethostname()
        try:
            self.peer_server_hostname = gethostbyname(hostname)
        except gaierror:
            colored_print("Couldn't get host name", "error")
            return

        my_ip = gethostname()
        self.udp_server_socket.bind((gethostbyname(my_ip), self.chat_room_server_port))
        self.tcp_server_socket.bind((self.peer_server_hostname, self.peer_server_port))

        self.tcp_server_socket.listen(4)

        sockets = [self.tcp_server_socket, self.udp_server_socket]

        while sockets and self.isOnline:
            try:
                read_sockets, write_sockets, error_sockets = select.select(sockets, [], [])
                for read_socket in read_sockets:
                    if read_socket == self.tcp_server_socket and not self.room:
                        tcp_socket, address = self.tcp_server_socket.accept()
                        tcp_socket.setblocking(0) # non-blocking socket
                        logging.info("Received connection from " + str(address))
                        sockets.append(tcp_socket)
                        if not self.isChatting:
                            colored_print(self.username + " is now connected with " + str(address), "success")
                            self.connected_peer_ip = address[0]
                            self.connected_peer_socket = tcp_socket
                    elif read_socket == self.udp_server_socket and self.room == 1: # handling udp messages
                        while True:
                            message, address = self.udp_server_socket.recvfrom(1024)
                            logging.info("Received message: " + message.decode() + " from " + str(address))
                            if not self.room:
                                break
                    elif not self.room:
                        # communication with the peer
                        message = read_socket.recv(1024).decode()
                        logging.info("Received message: " + str(message) + " from " + str(self.connected_peer_ip))
                        if str(message).split()[0].lower() == "create-private-chat-request":
                            if read_socket == self.connected_peer_socket:
                                message = message.split()
                                self.connected_peer_port = message[2]
                                self.connected_peer_username = message[1]
                                colored_print("Private chat request from " + self.connected_peer_username, "info")
                                colored_print("Type 'accept' to accept the request or 'reject' to reject it", "prompt")
                                self.isChatting = True
                            elif read_socket is not self.connected_peer_socket and self.isChatting:
                                response_message = "reject-connection " + message.split()[1] + " " + message.split()[2]
                                read_socket.send(response_message.encode())
                                sockets.remove(read_socket)
                        elif str(message).split()[0].lower() == "accept-connection":
                            self.isChatting = True
                        elif str(message).split()[0].lower() == "reject-connection":
                            self.isChatting = False
                            sockets.remove(read_socket)
                        elif len(str(message)) > 0:
                            # received a message from the peer
                            colored_print(str(self.connected_peer_username) + ": " + message, "menu")
                        elif str(message).split()[0].lower() == "end-connection":
                            colored_print("Connection ended with " + self.connected_peer_username, "info")
                            if self.room:
                                self.room = 0
                            else:
                                self.isChatting = False
                                sockets.clear()
                                sockets.append(self.tcp_server_socket)
                        elif len(str(message)) == 0:
                            colored_print("Connection ended with " + self.connected_peer_username, "info")
                            self.isChatting = False
                            sockets.clear()
                            sockets.append(self.tcp_server_socket)
            except OSError as e:
                # colored_print("Error: " + str(e), "error")
                logging.info("Error: " + str(e))
                break





