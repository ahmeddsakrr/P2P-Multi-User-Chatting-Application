from socket import *
import threading
import time
import select
import logging
from Service.color_utils import colored_print, colored_print_no_newline
import colorama
from Network.PeerServer import PeerServer

class PeerClient(threading.Thread):
    def __init__(self, connected_ip, connected_port, username, peer_server : PeerServer, received_response, choice, room_id, room_peers):

        threading.Thread.__init__(self)
        self.server_name = gethostbyname(gethostname())
        self.server_port = 15600
        self.connected_ip = connected_ip
        self.connected_port = connected_port
        self.username = username
        self.tcp_socket = socket(AF_INET, SOCK_STREAM)
        self.udp_socket = socket(AF_INET, SOCK_DGRAM)
        self.peer_server = peer_server
        # keeps the phrase that is used when creating the client
        # if the client is created with a phrase, it means this one received the request
        # this phrase should be none if this is the client of the requester peer
        self.received_response = received_response
        self.is_end = False
        self.choice = choice #flag to indicate room or normal chat
        self.room_id = room_id
        self.room_peers = room_peers
        self.is_room_empty = False


    def update_peers(self):
        message = "update-peers " + str(self.room_id)
        self.tcp_socket.send(message.encode())
        logging.info("Send to " + self.server_name + ":" + str(self.server_port) + " : " + message)
        response = self.tcp_socket.recv(1024).decode()
        updated_list_start = response.index("[")
        updated_list_end = response.index("]") + 1
        updated_list = response[updated_list_start:updated_list_end]
        # response = response.split()
        self.room_peers = eval(updated_list)

    def exit(self):
        colored_print("Leaving the chat room...", "success")
        removed_port = self.peer_server.chat_room_server_port
        request = "leave-room" + " " + str(self.room_id) + " " + str(removed_port) + " " + str(self.username)
        # print(request)
        # self.tcp_socket.send(request.encode())
        self.tcp_socket.send(request.encode())
        response = self.tcp_socket.recv(1024).decode()
        return response

    def run(self) -> None:
        if self.choice == '5':
            self.tcp_socket = socket(AF_INET, SOCK_STREAM)
            colored_print("Peer client started", "success")
            colored_print("Connecting to " + self.connected_ip + ":" + str(self.connected_port), "success")
            self.tcp_socket.connect((self.connected_ip, int(self.connected_port)))
            if not self.peer_server.isChatting and self.received_response is None:
                # if the server of this peer is not connected by someone else and if this is the requester side peer client then enters here
                request_message = "create-private-chat-request " + self.username + " " + str(self.peer_server.peer_server_port)
                logging.info("Send to " + self.connected_ip + ":" + str(self.connected_port) + " : " + request_message)

                self.tcp_socket.send(request_message.encode())
                colored_print("Waiting for response...", "success")
                self.received_response = self.tcp_socket.recv(1024).decode()
                logging.info("Received message: " + self.received_response + " from " + self.connected_ip + ":" + str(self.connected_port))
                colored_print("Received response: " + self.received_response, "success")
                self.received_response = self.received_response.split()
                if self.received_response[0] == "accept-connection":
                    # if response is ok then incoming messages will be evaluated as client messages and will be sent to the connected server
                    self.peer_server.isChatting = True
                    self.peer_server.connected_peer_username = self.received_response[1]
                    while self.peer_server.isChatting:
                        # as long as the server status is chatting, this client can send messages
                        sent_message = input()
                        self.tcp_socket.send(sent_message.encode())
                        logging.info("Send to " + self.connected_ip + ":" + str(self.connected_port) + " : " + sent_message)
                        if sent_message == "exit":
                            self.peer_server.isChatting = False
                            # self.peer_server.connected_peer_username = None
                            self.is_end = True
                            colored_print("Chat ended.", "success")
                            break

                    if not self.peer_server.isChatting:
                        # if peer is not chatting, checks if this is not the ending side
                        if not self.is_end:
                            # tries to send a quit message to the connected peer
                            # logs the message and handles the exception
                            try:
                                self.tcp_socket.send("exit".encode())
                                logging.info("Send to " + self.connected_ip + ":" + str(self.connected_port) + " : " + "exit")
                            except OSError as e:
                                colored_print("Error: " + str(e), "error")
                        self.tcp_socket.close()
                        self.received_response = None

                elif self.received_response[0] == "reject-connection":
                    # if the response is reject then the client will be closed
                    colored_print("Connection rejected.", "error")
                    self.tcp_socket.send("reject-connection".encode())
                    logging.info("Send to " + self.connected_ip + ":" + str(self.connected_port) + " : " + "reject-connection")
                    self.tcp_socket.close()
                elif self.received_response[0] == "busy":
                    colored_print("Peer Rejected the Connection", "error")
                    self.tcp_socket.close()
            elif self.received_response.split()[0] == "accept-connection":
                self.peer_server.isChatting = True
                response_sent = "accept-connection"
                self.tcp_socket.send(response_sent.encode())
                logging.info("Send to " + self.connected_ip + ":" + str(self.connected_port) + " : " + response_sent)
                colored_print("Private chat request accepted.", "success")
                while self.peer_server.isChatting:
                    # as long as the server status is chatting, this client can send messages
                    sent_message = input()
                    self.tcp_socket.send(sent_message.encode())
                    logging.info("Send to " + self.connected_ip + ":" + str(self.connected_port) + " : " + sent_message)
                    if sent_message == "exit":
                        self.peer_server.isChatting = False
                        # self.peer_server.connected_peer_username = None
                        self.is_end = True
                        colored_print("Chat ended.", "success")
                        break

                if not self.peer_server.isChatting:
                    # if peer is not chatting, checks if this is not the ending side
                    if not self.is_end:
                        # tries to send a quit message to the connected peer
                        # logs the message and handles the exception
                        try:
                            self.tcp_socket.send("exit".encode())
                            logging.info("Send to " + self.connected_ip + ":" + str(self.connected_port) + " : " + "exit")
                        except OSError as e:
                            # colored_print("Error: " + str(e), "error")
                            logging.error("Error: " + str(e))
                    self.tcp_socket.close()
                    self.received_response = None

        elif self.choice == "7":
            self.tcp_socket.connect((self.server_name, self.server_port))
            colored_print("Chat Room Client Started", "success")
            for peer in self.room_peers:
                if int(peer) != self.peer_server.chat_room_server_port:
                    # we don't want to send the message to the server
                    self.udp_socket.sendto(f"{self.username} joined the chat room".encode(), (self.connected_ip, int(peer)))
            while True:
                self.update_peers()
                if not self.room_peers:
                    break
                # colored_print_no_newline("You: ", "prompt")
                message_to_send = input()
                # add my username to the message
                message_to_send_to_peers = f"{self.username}: {message_to_send}"
                self.update_peers()

                if len(message_to_send) and message_to_send == "exit":
                    if self.exit() == "exit-success":
                        message_to_send_to_peers = f"{self.username} left the chat room"
                        for peer in self.room_peers:
                            if int(peer) != self.peer_server.chat_room_server_port:
                                # we don't want to send the message to the server
                                self.udp_socket.sendto(message_to_send_to_peers.encode(), (self.connected_ip, int(peer)))
                        # remove myself from their peers
                        self.room_peers.remove(str(self.peer_server.chat_room_server_port))
                        break

                else:
                    for peer in self.room_peers:
                        if int(peer) != self.peer_server.chat_room_server_port:
                            # we don't want to send the message to the server
                            self.udp_socket.sendto(message_to_send_to_peers.encode(), (self.connected_ip, int(peer)))

            colored_print("Chat Room Client Ended", "success")
            self.choice = None
            self.tcp_socket.close()

