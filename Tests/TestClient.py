import unittest
from unittest.mock import patch
from io import StringIO
from Client.client import Client

class TestClient(unittest.TestCase):

    def setUp(self):
        self.client = Client()

    def tearDown(self):
        pass

    @patch('builtins.input', side_effect=['1', 'test_user', 'test_password', '2', 'test_user', 'test_password', '3'])
    def test_client_interaction(self, mock_input):
        # This test simulates a sequence of user inputs: create account, login, logout
        with patch('sys.stdout', new=StringIO()) as fake_output:
            self.client.start()

            expected_output = "Account created successfully.\nLogin successful.\nLogged out successfully.\n"
            self.assertEqual(fake_output.getvalue(), expected_output)

    @patch('builtins.input', side_effect=['1', 'test_user', 'test_password', '1', 'test_user', 'test_password', '3'])
    def test_duplicate_account_creation(self, mock_input):
        # Test account creation when the username already exists
        with patch('sys.stdout', new=StringIO()) as fake_output:
            self.client.start()

            expected_output = "Account created successfully.\nAccount creation failed. Username already exists.\nLogged out successfully.\n"
            self.assertEqual(fake_output.getvalue(), expected_output)

    @patch('builtins.input', side_effect=['1', 'test_user', 'test_password', '2', 'wrong_user', 'test_password', '3'])
    def test_wrong_username_login(self, mock_input):
        # Test login with wrong username
        with patch('sys.stdout', new=StringIO()) as fake_output:
            self.client.start()

            expected_output = "Account created successfully.\nLogin failed. Wrong username.\nLogged out successfully.\n"
            self.assertEqual(fake_output.getvalue(), expected_output)

    @patch('builtins.input', side_effect=['1', 'test_user', 'test_password', '2', 'test_user', 'wrong_password', '3'])
    def test_wrong_password_login(self, mock_input):
        # Test login with wrong password
        with patch('sys.stdout', new=StringIO()) as fake_output:
            self.client.start()

            expected_output = "Account created successfully.\nLogin failed. Wrong password.\nLogged out successfully.\n"
            self.assertEqual(fake_output.getvalue(), expected_output)

    @patch('builtins.input', side_effect=['2', 'test_user', 'test_password', '1', 'test_user', 'test_password', '3'])
    def test_login_when_already_logged_in(self, mock_input):
        # Test login when user is already logged in
        with patch('sys.stdout', new=StringIO()) as fake_output:
            self.client.start()

            expected_output = "Login failed. User is already logged in.\nAccount created successfully.\nLogged out successfully.\n"
            self.assertEqual(fake_output.getvalue(), expected_output)

    @patch('builtins.input', side_effect=['3'])
    def test_logout_when_not_logged_in(self, mock_input):
        # Test logout when user is not logged in
        with patch('sys.stdout', new=StringIO()) as fake_output:
            self.client.start()

            expected_output = "Logout failed. User is not logged in.\nLogged out successfully.\n"
            self.assertEqual(fake_output.getvalue(), expected_output)

    @patch('builtins.input', side_effect=['1', 'test_user', 'test_password', '2', 'test_user', 'test_password', '3'])
    def test_logout_when_logged_in(self, mock_input):
        # Test logout when user is logged in
        with patch('sys.stdout', new=StringIO()) as fake_output:
            self.client.start()

            expected_output = "Account created successfully.\nLogin successful.\nLogged out successfully.\n"
            self.assertEqual(fake_output.getvalue(), expected_output)


if __name__ == '__main__':
    unittest.main()
