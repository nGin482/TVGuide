
from unittest import TestCase
from unittest.mock import MagicMock, patch

from database.models.User import User
from tests.test_data.users import users


class TestUserModel(TestCase):

    def setUp(self) -> None:
        return super().setUp()
    
    @patch('sqlalchemy.orm.session')
    def test_user_search_returns_all(self, mock_session: MagicMock):
        mock_session.scalars.return_value = users

        user_list = User.get_all_users(mock_session)
        
        self.assertEqual(len(user_list), 3)
        self.assertEqual(user_list[0].username, "John Smith")
        self.assertEqual(user_list[1].username, "Lelouch vi Britannia")
        self.assertEqual(user_list[2].username, "Megatron")

    @patch('sqlalchemy.orm.session')
    def test_user_search_returns_given_user(self, mock_session: MagicMock):
        mock_session.scalar.return_value = users[0]

        user = User.search_for_user("John Smith", mock_session)
        
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "John Smith")

    @patch('sqlalchemy.orm.session')
    def test_user_search_returns_none(self, mock_session: MagicMock):
        mock_session.scalar.return_value = None

        user = User.search_for_user("Optimus Prime", mock_session)
        
        self.assertIsNone(user)

    @patch('sqlalchemy.orm.session')
    def test_user_adds_user(self, mock_session: MagicMock):
        mock_session.add.return_value = ["added"]

        user = User(
            "Harold Finch",
            "person-of-interest"
        )

        user.add_user(mock_session)
        
        mock_session.add.assert_called()
        mock_session.commit.assert_called()

    @patch('sqlalchemy.orm.session')
    def test_user_deletes_user(self, mock_session: MagicMock):
        mock_session.delete.return_value = ["deleted"]

        user = User(
            "Harold Finch",
            "person-of-interest"
        )

        user.delete_user(mock_session)
        
        mock_session.delete.assert_called()
        mock_session.commit.assert_called()

    @patch('bcrypt.hashpw')
    def test_user_encrypts_password(self, mock_bcrypt: MagicMock):
        mock_bcrypt.return_value = "xxxx-xxxx-xxxx".encode()

        user = User(
            "Harold Finch",
            "person-of-interest"
        )

        encrypted_password = user.encrypt_password("person-of-interest")
        
        self.assertNotEqual(encrypted_password, "person-of-interest")
        self.assertEqual(encrypted_password, "xxxx-xxxx-xxxx")

    @patch('bcrypt.checkpw')
    def test_user_check_password_true(self, mock_bcrypt: MagicMock):
        mock_bcrypt.return_value = True

        user = User(
            "Harold Finch",
            "person-of-interest"
        )

        self.assertTrue(user.check_password("person-of-interest"))

    @patch('bcrypt.checkpw')
    def test_user_check_password_false(self, mock_bcrypt: MagicMock):
        mock_bcrypt.return_value = False

        user = User(
            "Harold Finch",
            "person-of-interest"
        )

        self.assertFalse(user.check_password("person-of-interest"))

    @patch('bcrypt.hashpw')
    def test_user_change_password(self, mock_bcrypt: MagicMock):
        mock_bcrypt.side_effect = ["xxxx-xxxx-xxxx".encode(), "xxxx-xxxx-yyyy".encode()]

        user = User(
            "Harold Finch",
            "person-of-interest"
        )

        original_password = user.password

        user.change_password("the-machine")

        self.assertNotEqual(user.password, "person-of-interest")
        self.assertNotEqual(user.password, original_password)
        self.assertNotEqual(user.password, "the-machine")

    def test_user_role_promotion(self):

        user = User(
            "Harold Finch",
            "person-of-interest"
        )

        self.assertEqual(user.role, "User")

        user.promote_role()

        self.assertEqual(user.role, "Admin")

    @patch('bcrypt.hashpw')
    def test_user_dict(self, mock_bcrypt: MagicMock):
        mock_bcrypt.return_value = "xxxx-xxxx-xxxx".encode()

        user = User(
            "Harold Finch",
            "person-of-interest"
        )

        user_dict = user.to_dict()

        self.assertEqual(user_dict['username'], "Harold Finch")
        self.assertEqual(user_dict['role'], "User")
        self.assertEqual(len(user_dict['show_subscriptions']), 0)
    