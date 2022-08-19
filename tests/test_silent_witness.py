import unittest
from database.models.GuideShow import SilentWitness

class TestSilentWitness(unittest.TestCase):

    def setUp(self) -> None:
        self.example_shows = ["Brother's Keeper - Part 1", "Bad Love (Part 2)", "Maters of Life and Death Part 1", "Redemption Part 1"]
        self.silent_witness_shows = [SilentWitness.handle('', 0, episode_title) for episode_title in self.example_shows]
    
    
    
    def test_silent_witness(self):
        example_shows = ["Brother's Keeper - Part 1", "Bad Love (Part 2)", "Maters of Life and Death Part 1", "Redemption Part 1"]
        self.assertEqual(sum([1, 2, 3]), 6)
        silent_witness_shows = [SilentWitness.handle('', 0, episode_title) for episode_title in example_shows]
        
        first_show = silent_witness_shows[0]
        second_show = silent_witness_shows[1]
        third_show = silent_witness_shows[2]
        fourth_show = silent_witness_shows[3]
         
        self.assertIsInstance(first_show, tuple)
        self.assertEqual(5, len(first_show))
        self.assertEqual('24', first_show[2])
        self.assertEqual(7, first_show[3])
        self.assertEqual("Brother's Keeper - Part 1", first_show[4])

        self.assertIsInstance(second_show, tuple)
        self.assertEqual(5, len(second_show))
        self.assertEqual('24', second_show[2])
        self.assertEqual(4, second_show[3])
        self.assertEqual("Bad Love (Part 2)", second_show[4])

        with self.assertRaises(ValueError):
            SilentWitness.handle('', 0, "Maters of Life and Death Part 1")
        # self.assertEqual('Episode not in Season 24', str(ctx.exception))