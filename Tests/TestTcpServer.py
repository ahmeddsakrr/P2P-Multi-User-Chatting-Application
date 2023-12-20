import unittest
from unittest.mock import MagicMock
from Network.tcp_server import TCPServer
class TestTCPServer(unittest.TestCase):

    def setUp(self):
        self.mock_tcp_socket = MagicMock()

    def test_create_account_user_exists(self):
        # Simulating a user existing in the database
        self.mock_tcp_socket.recv.return_value = "create username password".encode()
        db_mock = self.mock_tcp_socket.DatabaseAccess.return_value
        db_mock.user_exists.return_value = True  # Simulate user exists

        server = TCPServer('127.0.0.1', 12345, self.mock_tcp_socket)
        server.run()

        self.mock_tcp_socket.send.assert_called_with('create-failed-user-exists'.encode())

    def test_create_account_success(self):
        # Simulating a new user account creation
        self.mock_tcp_socket.recv.return_value = "create newuser newpassword".encode()
        db_mock = self.mock_tcp_socket.DatabaseAccess.return_value
        db_mock.user_exists.return_value = False  # Simulate user does not exist

        server = TCPServer('127.0.0.1', 12345, self.mock_tcp_socket)
        server.run()

        self.mock_tcp_socket.send.assert_called_with('create-success'.encode())

    def test_login_invalid_user(self):
        # Simulating login with an invalid user
        self.mock_tcp_socket.recv.return_value = "login invaliduser invalidpassword".encode()
        db_mock = self.mock_tcp_socket.DatabaseAccess.return_value
        db_mock.user_exists.return_value = False  # Simulate user does not exist

        server = TCPServer('127.0.0.1', 12345, self.mock_tcp_socket)
        server.run()

        self.mock_tcp_socket.send.assert_called_with('login-failed-username-not-found'.encode())

    def test_login_invalid_password(self):
        # Simulating login with invalid password
        self.mock_tcp_socket.recv.return_value = "login validuser wrongpassword".encode()
        db_mock = self.mock_tcp_socket.DatabaseAccess.return_value
        db_mock.user_exists.return_value = True
        db_mock.get_password.return_value = "valid_password_hash"  # Simulate valid password hash

        server = TCPServer('127.0.0.1', 12345, self.mock_tcp_socket)
        server.run()

        self.mock_tcp_socket.send.assert_called_with('login-failed-incorrect-password'.encode())

    def test_login_already_logged_in(self):
        # Simulating login when the user is already logged in
        self.mock_tcp_socket.recv.return_value = "login loggedinuser password".encode()
        db_mock = self.mock_tcp_socket.DatabaseAccess.return_value
        db_mock.user_exists.return_value = True
        db_mock.is_user_online.return_value = True  # Simulate user is already logged in

        server = TCPServer('127.0.0.1', 12345, self.mock_tcp_socket)
        server.run()

        self.mock_tcp_socket.send.assert_called_with('login-failed-already-logged-in'.encode())

    def test_logout_success(self):
        # Simulating logout of a logged-in user
        self.mock_tcp_socket.recv.return_value = "log-out validuser".encode()
        db_mock = self.mock_tcp_socket.DatabaseAccess.return_value
        db_mock.user_exists.return_value = True
        db_mock.is_user_online.return_value = True  # Simulate user is logged in

        server = TCPServer('127.0.0.1', 12345, self.mock_tcp_socket)
        server.run()

        self.mock_tcp_socket.send.assert_called_with('log-out-successvaliduser'.encode())


if __name__ == '__main__':
    unittest.main()
