from unittest.mock import MagicMock, patch
import unittest
import logging

from services.TVGuideScheduler import TVGuideScheduler


class TestTVGuideScheduler(unittest.TestCase):

    @classmethod
    def setUpClass(self) -> None:
        super().setUpClass()
        logging.disable()

    @patch('services.TVGuideScheduler.AsyncIOScheduler')
    def test_scheduler_initialisation(self, mock_scheduler: MagicMock):
        scheduler = TVGuideScheduler()
        self.assertFalse(scheduler.scheduler_initialised)

        scheduler.initialise()

        self.assertTrue(scheduler.scheduler_initialised)
        