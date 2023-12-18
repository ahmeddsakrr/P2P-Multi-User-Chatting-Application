from pymongo import MongoClient


class DatabaseAccess:

    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['p2p_database']

    def get_db(self):
        return self.db

    def get_client(self):
        return self.client

    def user_exists(self, username):
        return self.db.user.find_one({'username': username}) is not None

    def create_user(self, username, password):
        if not self.user_exists(username):
            self.db.user.insert_one({'username': username, 'password': password})
            return True
        return False

    def get_user(self, username):
        return self.db.user.find_one({'username': username})

    def get_password(self, username):
        return self.db.user.find_one({'username': username})['password']

    def set_password(self, username, password):
        self.db.user.update_one({'username': username}, {'$set': {'password': password}})

    def is_user_online(self, username):
        return self.db.online_users.find_one({'username': username}) is not None

    def set_user_online(self, username, port, ip):
        if not self.is_user_online(username):
            self.db.online_users.insert_one({'username': username, 'port': port, 'ip': ip})

    def set_user_offline(self, username):
        self.db.online_users.delete_one({'username': username})
    
    def get_user_ip(self, username):
        return self.db.online_users.find_one({'username': username})['ip']
    
    def get_user_port(self, username):
        return self.db.online_users.find_one({'username': username})['port']
    
    def get_online_users(self):
        return self.db.online_users.find()
    
    def get_online_users_list(self):
        return [user['username'] for user in self.get_online_users()]