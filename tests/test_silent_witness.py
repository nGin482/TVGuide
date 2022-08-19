import unittest
from database.models.GuideShow import SilentWitness

class TestSilentWitness(unittest.TestCase):

    def test_silent_witness(self):
        first_show = SilentWitness.handle('', 0, "Brother's Keeper - Part 1")
        second_show = SilentWitness.handle('', 0, "Bad Love (Part 2)")
        fourth_show = SilentWitness.handle('', 0, "Redemption Part 1")
         
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

        self.assertRaises(ValueError, SilentWitness.handle, '', 0, "Maters of Life and Death Part 1")

        self.assertIsInstance(fourth_show, tuple)
        self.assertEqual(5, len(fourth_show))
        self.assertEqual('24', fourth_show[2])
        self.assertEqual(1, fourth_show[3])
        self.assertEqual("Redemption Part 1", fourth_show[4])
            
        # self.assertEqual('Episode not in Season 24', str(ctx.exception))