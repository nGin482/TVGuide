import unittest
from database.models.GuideShowCases import SilentWitness

class TestSilentWitness(unittest.TestCase):

    def test_silent_witness(self):
        first_show = SilentWitness.handle("Brother's Keeper - Part 1")
        second_show = SilentWitness.handle("Bad Love (Part 2)")
        fourth_show = SilentWitness.handle("Redemption Part 1")
         
        self.assertIsInstance(first_show, tuple)
        self.assertEqual(4, len(first_show))
        self.assertEqual('24', first_show[1])
        self.assertEqual(7, first_show[2])
        self.assertEqual("Brother's Keeper - Part 1", first_show[3])

        self.assertIsInstance(second_show, tuple)
        self.assertEqual(4, len(second_show))
        self.assertEqual('24', second_show[1])
        self.assertEqual(4, second_show[2])
        self.assertEqual("Bad Love (Part 2)", second_show[3])

        self.assertIsInstance(fourth_show, tuple)
        self.assertEqual(4, len(fourth_show))
        self.assertEqual('24', fourth_show[1])
        self.assertEqual(1, fourth_show[2])
        self.assertEqual("Redemption Part 1", fourth_show[3])

    def test_silent_witness_return_none(self):
        self.assertIsNone(SilentWitness.handle("Maters of Life, Death Part 1"))

            
        # self.assertEqual('Episode not in Season 24', str(ctx.exception))