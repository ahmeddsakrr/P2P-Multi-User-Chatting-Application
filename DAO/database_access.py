from pymongo import MongoClient, errors
from Service.color_utils import colored_print
import colorama

class DatabaseAccess:

    def __init__(self):
        try:
            colorama.init()
            self.client = MongoClient('localhost', 27017)
            self.db = self.client['p2p_database']
        except errors.ConnectionFailure as e:
            colored_print("Could not connect to MongoDB: %s" % e, "error")

    def get_db(self):
        """
        Returns the MongoDB database object.
        """
        return self.db

    def get_client(self):
        """
        Returns the MongoClient object for the database connection.
        """
        return self.client


    def user_exists(self, username):
        """
            Checks if a user exists in the database.

            Parameters:
            - username (str): The username to check.

            Returns:
            - bool: True if the user exists, False otherwise.
        """
        try:

            return self.db.user.find_one({'username': username}) is not None
        except errors.PyMongoError as e:
            colored_print("Error checking user existence : %s" % e, "error")

    def create_user(self, username, password, salt):
        """
        Creates a new user in the database.

        Parameters:
        - username (str): The username of the new user.
        - password (str): The (hashed) password of the new user.

        Returns:
        - bool: True if the user is created successfully, False if the user already exists.
        """
        try:

            if not self.user_exists(username):
                self.db.user.insert_one({'username': username, 'password': password, 'salt': salt})
                return True
        except errors.PyMongoError as e:
            colored_print("Error creating user : %s" % e, "error")
            return False

    def get_user(self, username):
        """
        Retrieves user information from the database.

        Parameters:
        - username (str): The username of the user to retrieve.

        Returns:
        - Object: User information if found, else None.
        """
        return self.db.user.find_one({'username': username})

    def get_password(self, username):
        """
        Retrieves the password of a user from the database.

        Parameters:
        - username (str): The username of the user.

        Returns:
        - str: The password of the user.
        """
        return self.db.user.find_one({'username': username})['password'] if self.user_exists(username) else None

    def set_password(self, username, password):
        """
        Updates the password of a user in the database.

        Parameters:
        - username (str): The username of the user.
        - password (str): The new password to set.
        """
        self.db.user.update_one({'username': username}, {'$set': {'password': password}})

    def is_user_online(self, username):
        """
        Checks if a user is currently online.

        Parameters:
        - username (str): The username of the user.

        Returns:
        - bool: True if the user is online, False otherwise.
        """
        return self.db.online_users.find_one({'username': username}) is not None

    def set_user_online(self, username, port, ip):
        """
        Sets a user as online in the database.

        Parameters:
        - username (str): The username of the user.
        - port (int): The port number of the user.
        - ip (str): The IP address of the user.
        """
        try:
            if not self.is_user_online(username):
                self.db.online_users.insert_one({'username': username, 'port': port, 'ip': ip})
        except errors.PyMongoError as e:
            colored_print("Error setting user online : %s" % e, "error")

    def set_user_offline(self, username):
        """
        Sets a user as offline in the database.

        Parameters:
        - username (str): The username of the user.
        """
        try:
            self.db.online_users.delete_one({'username': username})
        except errors.PyMongoError as e:
            colored_print("Error setting user offline : %s" % e, "error")

    def get_user_ip(self, username):
        """
        Retrieves the IP address of a user from the database.

        Parameters:
        - username (str): The username of the user.

        Returns:
        - str: The IP address of the user.
        """
        return self.db.online_users.find_one({'username': username})['ip'] if self.is_user_online(username) else None
    
    def get_user_port(self, username):
        """
        Retrieves the port number of a user from the database.

        Parameters:
        - username (str): The username of the user.

        Returns:
        - int: The port number of the user.
        """
        return self.db.online_users.find_one({'username': username})['port'] if self.is_user_online(username) else None
    
    def get_online_users(self):
        """
        Retrieves all online users from the database.

        Returns:
        - pymongo.cursor.Cursor: Cursor object containing online users' information.
        """
        return self.db.online_users.find()
    
    def get_online_users_list(self):
        """
        Retrieves a list of usernames of all online users.

        Returns:
        - list: List of usernames of online users.
        """
        return [user['username'] for user in self.get_online_users()]

    def get_user_salt(self, username):
        """
        Retrieves the salt of a user from the database.

        Parameters:
        - username (str): The username of the user.

        Returns:
        - str: The salt of the user.
        """
        return self.db.user.find_one({'username': username})['salt'] if self.user_exists(username) else None

    def create_chat_room(self, room_name):
        """
        Creates a new chat room in the database.

        Parameters:
        - room_name (str): The name of the chat room.

        Returns:
        - bool: True if the chat room is created successfully, False if the chat room already exists.
        """
        try:
            if not self.chat_room_exists(room_name):
                self.db.rooms.insert_one({'room_name': room_name, 'users': []})
                return True
            else:
                return False
        except errors.PyMongoError as e:
            colored_print("Error creating chat room: %s" % e, "error")
            return False

    def join_chat_room(self, room_name, username):
        """
        Adds a user to a chat room in the database.

        Parameters:
        - room_name (str): The name of the chat room.
        - username (str): The username of the user joining the chat room.

        Returns:
        - bool: True if the user is added to the chat room successfully, False if the chat room or user does not exist.
        """
        try:
            if self.chat_room_exists(room_name) and self.user_exists(username):
                self.db.rooms.update_one({'room_name': room_name}, {'$addToSet': {'users': username}})
                return True
            else:
                return False
        except errors.PyMongoError as e:
            colored_print("Error joining chat room: %s" % e, "error")
            return False

    def chat_room_exists(self, room_name):
        """
        Checks if a chat room exists in the database.

        Parameters:
        - room_name (str): The name of the chat room.

        Returns:
        - bool: True if the chat room exists, False otherwise.
        """
        try:
            return self.db.rooms.find_one({'room_name': room_name}) is not None
        except errors.PyMongoError as e:
            colored_print("Error checking chat room existence: %s" % e, "error")
            return False

    def get_chat_rooms(self):
        """
        Retrieves a list of all chat rooms.

        Returns:
        - list: List of chat room names.
        """
        return [room['room_name'] for room in self.db.rooms.find()]
        # return self.db.rooms.find()

    def get_chat_room_users(self, room_name):
        """
        Retrieves a list of all users in a chat room.

        Parameters:
        - room_name (str): The name of the chat room.

        Returns:
        - list: List of usernames of users in the chat room.
        """
        return self.db.rooms.find_one({'room_name': room_name})['users'] if self.chat_room_exists(room_name) else None

    def get_chat_room_users_list(self, room_name):
        """
        Retrieves a list of all users in a chat room.

        Parameters:
        - room_name (str): The name of the chat room.

        Returns:
        - list: List of usernames of users in the chat room.
        """
        return [user['username'] for user in self.get_chat_room_users(room_name)]

    def delete_room(self, room_name):
        """
        Deletes a chat room from the database.

        Parameters:
        - room_name (str): The name of the chat room.
        """
        self.db.rooms.delete_one({'room_name': room_name})

    def remove_user_from_room(self, room_name, username):
        """
        Removes a user from a chat room.

        Parameters:
        - room_name (str): The name of the chat room.
        - username (str): The username of the user to remove.
        """
        self.db.rooms.update_one({'room_name': room_name}, {'$pull': {'users': username}})

    def get_chat_room_peers(self, room_name):
        result = self.db.rooms.find_one({'room_name': room_name})
        return result["room_name"], result["users"] # return the id of the room and the users in the room

    def update_chat_room_peers(self, room_name, peers):
        self.db.rooms.update_one({'room_name': room_name}, {'$set': {'users': peers}})
