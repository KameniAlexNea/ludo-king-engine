"""Tests for the simplified engine constants."""

import unittest

from ludo_engine import CONFIG


class TestConstants(unittest.TestCase):
    def test_total_steps_matches_track_and_home_run(self) -> None:
        self.assertEqual(CONFIG.travel_distance, CONFIG.track_size - 1)
        self.assertEqual(CONFIG.total_steps, CONFIG.travel_distance + CONFIG.home_run)

    def test_home_positions_are_safe(self) -> None:
        for position in CONFIG.home_positions:
            self.assertIn(position, CONFIG.safe_positions)

    def test_all_colors_share_same_home_lane(self) -> None:
        lanes = {tuple(values) for values in CONFIG.home_columns.values()}
        self.assertEqual(len(lanes), 1)
        lane = lanes.pop()
        self.assertEqual(lane[0], 100)
        self.assertEqual(len(lane), CONFIG.home_run)


if __name__ == "__main__":
    unittest.main()
