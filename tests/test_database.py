from database.users_collection import users_collection, get_all_users, create_user, add_show_for_user
import mongomock
import unittest

# python3 -m unittest discover

class TestDatabase(unittest.TestCase):
    mongo_client = mongomock.MongoClient().tvguide
    showlist_collection = mongo_client.ShowList
    recorded_shows_collection = mongo_client.RecordedShows
    reminders_collection = mongo_client.Reminders
    users_collection = mongo_client.Users
    
    @classmethod
    def setUpClass(cls):
        user = {
            'userID': '1234567',
            'username': 'Test',
            'password': 'pass',
            'shows': [],
            'reminders': []
        }

    def test_get_showlist_empty(self):
        """
        """
        get_searchlist = [show for show in self.showlist_collection.find({})]
        self.assertEqual([], get_searchlist)

    def test_add_show_to_searchlist(self):
        pass
        
    
    def test_users_collection(self):
        """
        Test the Collection object returned for registered users
        """

        collection = users_collection()

        self.assertNotIsInstance(collection, list, 'The collection object cannot be returned')
    
    def test_get_users(self):
        """
        Test the ability to retrieve users from the collection
        """

        users = get_all_users()

        self.assertNotEqual(len(users), 0, 'No users were retrieved')
    
    def test_create_user(self):
        """
        Test that a new user can be created and inserted into the DB
        """

        user = {
            'userID': '',
            'username': 'Rango',
            'password': 'pass',
            'searchList': [],
            'reminders': []
        }

        self.assertIsNotNone(user['userID'], 'The userID cannot be a NONE value')
        self.assertNotEqual(user['username'], '', 'The username given cannot be empty')
        self.assertNotEqual(user['password'], '', 'The password given cannot be empty')

        new_user = create_user(user)
        self.assertEqual(new_user['status'], True, 'Creating a user did not work')

    def test_add_to_search_list(self):
        """
        Test that a show can be added to a user's search list
        """

        insert_show_status = add_show_for_user('Bob', 'Maigret')

        self.assertTrue(insert_show_status['status'])
        self.assertEqual(len(insert_show_status.keys()), 2, 'Inserting a show returned did not return 2 key value pairs')
        self.assertTrue('status' in insert_show_status.keys(), "The returned dict should have a 'status' key")
        self.assertTrue('message' in insert_show_status.keys(), "The returned dict should have a 'message' key")
        self.assertTrue('Maigret' in insert_show_status['message'], 'The message returned should include the show being added')

    @classmethod
    def tearDownClass(cls):
        users_collection().delete_one({'username': 'Test'})
        users_collection().delete_one({'username': 'Rango'})


if __name__ == '__main__':
    unittest.main()