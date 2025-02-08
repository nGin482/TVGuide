
from unittest import TestCase
from unittest.mock import MagicMock, patch

from database.models.UserSearchSubscriptionModel import UserSearchSubscription
from tests.test_data.search_items import search_items
from tests.test_data.users import users

class TestUserSearchSubscription(TestCase):

    def setUp(self) -> None:
        return super().setUp()
    
    @patch('database.models.UserSearchSubscription.search_item')
    @patch('database.models.UserSearchSubscription.user')
    @patch('sqlalchemy.orm.session')
    def test_user_search_subscription_add(
        self,
        mock_session: MagicMock,
        mock_user: MagicMock,
        mock_search_item: MagicMock
    ):
        mock_session.add.return_value = "added"
        mock_user.return_value = users[0]
        mock_search_item.return_value = search_items[0]

        user_sub = UserSearchSubscription(
            1,
            10
        )
        user_sub.add_subscription(mock_session)

        mock_session.add.assert_called()
        mock_session.commit.assert_called()

    @patch('database.models.UserSearchSubscription.search_item')
    @patch('database.models.UserSearchSubscription.user')
    @patch('sqlalchemy.orm.session')
    def test_user_search_subscription_remove(
        self,
        mock_session: MagicMock,
        mock_user: MagicMock,
        mock_search_item: MagicMock
    ):
        mock_session.delete.return_value = "deleted"
        mock_user.return_value = users[0]
        mock_search_item.return_value = search_items[0]
        

        user_sub = UserSearchSubscription(
            1,
            10
        )
        user_sub.remove_subscription(mock_session)

        mock_session.delete.assert_called()
        mock_session.commit.assert_called()

    def test_user_search_subscription_dict(self):
        user_sub = UserSearchSubscription(
            1,
            10
        )
        user_sub.search_item = search_items[0]

        user_sub_dict = user_sub.to_dict()

        self.assertEqual(user_sub_dict['user_id'], 1)
        self.assertEqual(user_sub_dict['search_item_id'], 10)
