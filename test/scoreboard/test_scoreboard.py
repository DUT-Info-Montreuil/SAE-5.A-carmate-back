import unittest

from api.worker.scoreboard.use_case import *

class ScoreboardTestCase(unittest.TestCase):
    def setUp(self):
        self.get_best_economic_driving_rating = GetBestEconomicDrivingRating()
        self.get_best_safe_driving_rating = GetBestSafeDrivingRating()
        self.get_best_sociability_rating = GetBestSociabilityRating()

    def test_get_best_economic_driving_rating(self):
        scores = self.get_best_economic_driving_rating.worker()
        self.assertEqual(scores[0].driver_id, 1)

    def test_best_safe_driving_rating(self):
        scores = self.get_best_safe_driving_rating.worker()
        self.assertEqual(scores[0].driver_id, 0)

    def test_get_best_sociability_rating(self):
        scores = self.get_best_sociability_rating.worker()
        self.assertEqual(scores[0].driver_id, 2)
