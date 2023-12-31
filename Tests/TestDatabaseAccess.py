import unittest
from DAO.database_access import DatabaseAccess

class TestDatabaseAccess(unittest.TestCase):

    def setUp(self):
        # Initialize DatabaseAccess for testing
        self.db_access = DatabaseAccess()

    def tearDown(self):
        # Clean up any resources after tests are run
        # For example, delete test users created during testing
        self.db_access.db.user.delete_many({'username': {'$in': ['test_user', 'new_user']}})
        self.db_access.db.online_users.delete_many({'username': {'$in': ['test_user', 'new_user']}})
        self.db_access.db.rooms.delete_many({'room_name': {'$in': ['test_room', 'new_room']}})

    def test_user_exists(self):
        # Test user existence when user exists
        self.assertTrue(self.db_access.create_user('test_user', 'password', ""))
        self.assertTrue(self.db_access.user_exists('test_user'))

        # Test user existence when user doesn't exist
        self.assertFalse(self.db_access.user_exists('non_existing_user'))

    def test_create_user(self):
        # Test creating a new user
        self.assertTrue(self.db_access.create_user('new_user', 'password', ""))

        # Test creating an existing user
        self.assertFalse(self.db_access.create_user('new_user', 'password', ""))

    def test_get_user(self):
        # Test retrieving an existing user
        self.db_access.create_user('new_user', 'password', "")
        self.assertIsNotNone(self.db_access.get_user('new_user'))

        # Test retrieving a non-existing user
        self.assertIsNone(self.db_access.get_user('non_existing_user'))

    def test_get_password(self):
        # Test retrieving password for an existing user
        self.db_access.create_user('new_user', 'password', "")
        self.assertEqual(self.db_access.get_password('new_user'), 'password')

        # Test retrieving password for a non-existing user
        self.assertIsNone(self.db_access.get_password('non_existing_user'))


    def test_set_password(self):
        # Test setting password for an existing user
        self.db_access.create_user('test_user', 'old_password', "")
        self.db_access.set_password('test_user', 'new_password')
        self.assertEqual(self.db_access.get_password('test_user'), 'new_password')

    def test_user_status(self):
        # Test when user is online
        self.db_access.set_user_online('test_user', 8080, '127.0.0.1')
        self.assertTrue(self.db_access.is_user_online('test_user'))

        # Test when user is offline
        self.db_access.set_user_offline('test_user')
        self.assertFalse(self.db_access.is_user_online('test_user'))

    def test_get_user_ip(self):
        # Test retrieving IP for an existing user
        self.db_access.set_user_online('test_user', 8080, '127.0.0.1')
        self.assertEqual(self.db_access.get_user_ip('test_user'), '127.0.0.1')

        # Test retrieving IP for a non-existing user
        self.assertIsNone(self.db_access.get_user_ip('non_existing_user'))

    def test_get_user_port(self):
        # Test retrieving port for an existing user
        self.db_access.set_user_online('test_user', 8080, '127.0.0.1')
        self.assertEqual(self.db_access.get_user_port('test_user'), 8080)

        # Test retrieving port for a non-existing user
        self.assertIsNone(self.db_access.get_user_port('non_existing_user'))

    def test_get_online_users_list(self):
        # Test retrieving list of online users
        self.db_access.set_user_online('test_user', 8080, '127.0.0.1')
        self.db_access.set_user_online('new_user', 9090, '192.168.1.1')
        expected_users = ['test_user', 'new_user']
        self.assertCountEqual(self.db_access.get_online_users_list(), expected_users)

    def test_get_chat_rooms(self):
        # Test retrieving chat rooms when there are existing rooms
        self.db_access.create_chat_room('test_room')
        self.db_access.create_chat_room('new_room')
        expected_rooms = ['test_room', 'new_room']
        self.assertCountEqual(self.db_access.get_chat_rooms(), expected_rooms)

        # Test retrieving chat rooms when there are no rooms
        self.db_access.delete_room('test_room')
        self.db_access.delete_room('new_room')
        self.assertEqual(self.db_access.get_chat_rooms(), [])

    def test_chat_room_exists(self):
        # Test checking chat room existence when the room exists
        self.db_access.create_chat_room('test_room')
        self.assertTrue(self.db_access.chat_room_exists('test_room'))

        # Test checking chat room existence when the room doesn't exist
        self.assertFalse(self.db_access.chat_room_exists('non_existing_room'))

    def test_join_chat_room(self):
        # Test joining an existing chat room
        self.db_access.create_user('test_user', 'password', "")
        self.db_access.create_chat_room('test_room')
        self.assertTrue(self.db_access.join_chat_room('test_room', 'test_user'))

        # Test joining a non-existing chat room
        self.assertFalse(self.db_access.join_chat_room('non_existing_room', 'test_user'))

    def test_create_chat_room(self):
        # Test creating a new chat room
        self.assertTrue(self.db_access.create_chat_room('new_room'))

        # Test creating an existing chat room
        self.assertFalse(self.db_access.create_chat_room('new_room'))




if __name__ == '__main__':
    unittest.main()


