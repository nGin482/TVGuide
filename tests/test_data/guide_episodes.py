from datetime import datetime

from database.models.GuideEpisode import GuideEpisode

guide_episodes = [
    GuideEpisode(
        'Doctor Who',
        'ABC2',
        datetime(year=2024, month=8, day=10, hour=22, minute=4),
        datetime(year=2024, month=8, day=10, hour=22, minute=51),
        2,
        5,
        'Rise of the Cybermen',
        1,
        1,
        3,
        4
    ),
    GuideEpisode(
        'Endeavour',
        'ABC2',
        datetime(year=2024, month=8, day=10, hour=20, minute=30),
        datetime(year=2024, month=8, day=10, hour=22, minute=0),
        5,
        6,
        'Icarus',
        1,
        2,
        20,
        2
    )
]