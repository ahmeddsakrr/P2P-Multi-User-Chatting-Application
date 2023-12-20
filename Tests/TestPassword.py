import unittest
from Service.password import Password
class TestPassword(unittest.TestCase):

    def test_hash_and_verify(self):
        # Test hashing and verification of passwords
        password = "test_password"
        salt = Password.generate_salt()

        hashed_password = Password.hash(password, salt)
        self.assertTrue(Password.verify(hashed_password, password, salt))

        # Test verification with wrong password
        wrong_password = "wrong_password"
        self.assertFalse(Password.verify(hashed_password, wrong_password, salt))

        # Test verification with wrong salt
        wrong_salt = Password.generate_salt()
        self.assertFalse(Password.verify(hashed_password, password, wrong_salt))

    def test_generate_salt(self):
        # Test generating a salt
        salt1 = Password.generate_salt()
        salt2 = Password.generate_salt()

        # Ensure different salts are generated
        self.assertNotEqual(salt1, salt2)

        # Ensure the length of the salt is as expected
        self.assertEqual(len(salt1), 64)  # SHA-256 produces a 64-character hexadecimal string

    # Add more test methods for edge cases and other functionalities...

if __name__ == '__main__':
    unittest.main()
