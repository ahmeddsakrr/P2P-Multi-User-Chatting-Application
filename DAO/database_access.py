from pymongo import MongoClient, errors
from Service.color_utils import colored_print

class DatabaseAccess:

    def __init__(self):
        try:

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

    def create_user(self, username, password):
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
                self.db.user.insert_one({'username': username, 'password': password})
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