import hashlib
import os

class Password:
    @staticmethod
    def hash(password, salt):
        return hashlib.sha256(password.encode() + salt.encode()).hexdigest()

    @staticmethod
    def verify(stored_password, provided_password, salt):
        return stored_password == Password.hash(provided_password, salt)

    @staticmethod
    def generate_salt():
        return hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')