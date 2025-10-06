from datetime import datetime

from database.models.GuideModel import Guide

test_guides = [
    Guide(
        datetime(year=2024, month=8, day=10),
        None
    ),
    Guide(
        datetime(year=2024, month=8, day=11),
        None
    ),
]

for idx, guide in enumerate(test_guides):
    test_guides[idx].id = idx + 1